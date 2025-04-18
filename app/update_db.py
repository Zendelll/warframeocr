import json
import sqlite3
import requests
from app.db import add_item, DB_NAME


WARFRAME_API = "https://api.warframestat.us/wfinfo/filtered_items/"
MARKET_API = "https://api.warframe.market/v1/items/{item}/orders"


def update_db() -> None: 
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        response = requests.get(WARFRAME_API)
        items = json.loads(response.text)
        items = items["eqmt"]
        for set, parts in items.items():
            for item_name, item_stats in parts["parts"].items():
                if not "ducats" in item_stats:
                    continue

                item_data = {
                    "name": item_name,
                    "item_set": set,
                    "ducats": item_stats["ducats"],
                    "price": 0,
                }
                if parts["type"] == "Warframes" and "Blueprint" not in item_data["name"]:
                    item_data["name"] += " Blueprint"
                print(item_name.replace(" ", "_").lower())
                try:
                    url_item = item_name.replace(" ", "_").lower().replace("&", "and")
                    response = requests.get(MARKET_API.format(item=url_item))
                    orders = json.loads(response.text)["payload"]["orders"]
                except:
                    url_item = (
                        f"{item_name}_blueprint".replace(" ", "_")
                        .lower()
                        .replace("&", "and")
                    )
                    response = requests.get(MARKET_API.format(item=url_item))
                    orders = json.loads(response.text)["payload"]["orders"]
                orders = sorted(orders, key=lambda x: x["platinum"])
                orders = [
                    order
                    for order in orders
                    if order["order_type"] == "sell" and order["user"]["status"] == "ingame"
                ]
                orders = orders[:5]
                price = 0
                if orders:
                    for order in orders:
                        price += order["platinum"]
                    price = price / len(orders)
                item_data["price"] = round(price, 1)
                print(item_data)
                add_item(item_data, cursor)
        conn.commit()
    print("[INFO] DB updated")
