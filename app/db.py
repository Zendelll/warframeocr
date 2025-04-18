import sqlite3
import os
import dotenv

dotenv.load_dotenv()
DB_NAME = os.getenv("DB_NAME", "items.db")

INIT_DB = """CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    item_set TEXT NOT NULL,
    ducats INTEGER NOT NULL,
    price INTEGER DEFAULT 0,
    owned INTEGER DEFAULT 0
)"""

ADD_ITEM = """
INSERT INTO items (
    name, item_set, ducats, price, owned
    ) VALUES (?, ?, ?, ?, 0)
    ON CONFLICT(name) DO UPDATE SET
    item_set = excluded.item_set,
    ducats = excluded.ducats,
    price = excluded.price
"""


def init() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(INIT_DB)
        cursor.execute(
            """
        INSERT INTO items (
            name, item_set, ducats, price, owned
            ) VALUES ("Forma Blueprint", "Forma", 0, 0, 0)
            ON CONFLICT(name) DO UPDATE SET
            item_set = excluded.item_set,
            ducats = excluded.ducats,
            price = excluded.price
        """
        )
        conn.commit()
    print("[INFO] DB initialized")


def add_item(item: dict, cursor) -> None:
    cursor.execute(
        ADD_ITEM, (item["name"], item["item_set"], item["ducats"], item["price"])
    )


def get_item(item_name: str, cursor) -> list[tuple]:
    cursor.execute("SELECT * FROM items where name = ?;", (item_name,))
    return cursor.fetchall()


def get_all_item_names(cursor) -> list:
    cursor.execute("SELECT name FROM items")
    return cursor.fetchall()
