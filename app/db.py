import sqlite3
import os
import dotenv
import json
import requests
from app.models import Item
from itertools import islice


dotenv.load_dotenv()
DB_NAME = os.getenv("DB_NAME", "items.db")
DB_MEMORY_NAME = os.getenv("DB_MEMORY_NAME", "memory_db")
WARFRAME_API = "https://api.warframestat.us/wfinfo/filtered_items/"
MARKET_ITEM_API = "https://api.warframe.market/v1/items/{item}/statistics"
memory_conn = None

INIT_DB = """CREATE TABLE IF NOT EXISTS prime_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    item_set TEXT NOT NULL,
    ducats INTEGER NOT NULL,
    price INTEGER DEFAULT 0,
    sold INTEGER DEFAULT 0,
    vaulted INTEGER DEFAULT 0,
    item_set_price INTEGER DEFAULT 0,
    item_set_sold INTEGER DEFAULT 0,
    items_to_craft INTEGER DEFAULT 1,
    owned INTEGER DEFAULT 0,
    mastered INTEGER DEFAULT 0
)"""

ADD_ITEM = """INSERT INTO prime_items (
    name, item_set, ducats, price, sold, vaulted, item_set_price, item_set_sold, items_to_craft, owned, mastered
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(name) DO UPDATE SET
    item_set = excluded.item_set,
    ducats = excluded.ducats,
    price = excluded.price,
    sold = excluded.sold,
    vaulted = excluded.vaulted,
    item_set_price = excluded.item_set_price,
    item_set_sold = excluded.item_set_sold,
    items_to_craft = excluded.items_to_craft
"""


def init() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(INIT_DB)
        add_item(
            Item(name="Forma", item_set="Forma", ducats=0),
            cursor,
        )
    refresh_memory()
    print("[INFO] File db initialized")


def refresh_memory() -> None:
    global memory_conn
    with sqlite3.connect(DB_NAME) as conn_db:
        if memory_conn: memory_conn.close()
        memory_conn = sqlite3.connect(
            f"file:{DB_MEMORY_NAME}?mode=memory&cache=shared", uri=True
        )
        conn_db.backup(memory_conn)
    print("[INFO] Memory db initialized")

def close_memory() -> None:
    global memory_conn
    if memory_conn:
        memory_conn.close()
        memory_conn = None


def add_item(item: Item, cursor=None, refresh=False) -> None:
    """Add item to db

    Args:
        item (Item): item info
        cursor (Cursor, optional): cursor to use exsisting connection. Defaults to None.
        refresh (bool, optional): flag to refresh memory after adding item.
            If set to false, it's your responsibility to call refresh_memory(). Defaults to False.
    """
    close_connection = False
    if not cursor:
        close_connection = True
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
    cursor.execute(
        ADD_ITEM,
        (
            item.name,
            item.item_set,
            item.ducats,
            item.price,
            item.sold,
            item.vaulted,
            item.item_set_price,
            item.item_set_sold,
            item.items_to_craft,
            item.owned,
            item.mastered,
        ),
    )
    if close_connection:
        conn.commit()
        conn.close()
    print(f"[INFO] {item.name} added to db")
    if refresh:
        refresh_memory()


def get_item(item_name: str) -> Item | None:
    with sqlite3.connect(
        f"file:{DB_MEMORY_NAME}?mode=memory&cache=shared", uri=True
    ) as conn_mem:
        conn_mem.row_factory = sqlite3.Row
        cursor = conn_mem.cursor()
        cursor.execute("SELECT * FROM prime_items where name = ?;", (item_name,))
        row = cursor.fetchone()
        if row:
            return Item(**dict(row))
        return None


def get_all_item_names() -> list:
    with sqlite3.connect(
        f"file:{DB_MEMORY_NAME}?mode=memory&cache=shared", uri=True
    ) as conn_mem:
        cursor = conn_mem.cursor()
        cursor.execute("SELECT name FROM prime_items")
        return cursor.fetchall()


def update_db() -> None:
    def get_median_price(item_name: str, days=3) -> dict:
        response = requests.get(MARKET_ITEM_API.format(item=item_name))
        orders = json.loads(response.text)["payload"]["statistics_closed"]["90days"][
            -3:
        ]
        result = {"median": 0, "sold": 0}
        for stat in orders:
            result["median"] += stat["median"]
            result["sold"] += stat["volume"]
        result["median"] = round(result["median"] / days)
        result["sold"] = round(result["sold"] / days)
        return result

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        response = requests.get(WARFRAME_API)
        items = json.loads(response.text)
        items = items["eqmt"]
        for set, parts in items.items():
            set_market_info = get_median_price(
                f"{set.replace(" ", "_").lower().replace("&", "and")}_set"
            )
            for item_name, item_stats in parts["parts"].items():
                if "ducats" not in item_stats:
                    continue
                try:
                    item_market_info = get_median_price(
                        item_name.replace(" ", "_").lower().replace("&", "and")
                    )
                except:
                    item_market_info = get_median_price(
                        f"{item_name}_blueprint".replace(" ", "_")
                        .lower()
                        .replace("&", "and")
                    )

                print("\n")
                item = Item(
                    name=(
                        f"{item_name} Blueprint"
                        if parts["type"] == "Warframes" and "Blueprint" not in item_name
                        else item_name
                    ),
                    item_set=set,
                    ducats=item_stats["ducats"],
                    price=item_market_info["median"],
                    sold=item_market_info["sold"],
                    vaulted=item_stats["vaulted"],
                    item_set_price=set_market_info["median"],
                    item_set_sold=set_market_info["sold"],
                    items_to_craft=item_stats["count"],
                )
                print(item)
                add_item(item, cursor)
        conn.commit()
    print("[INFO] DB updated")
    refresh_memory()
