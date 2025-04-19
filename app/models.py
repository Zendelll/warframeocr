from pydantic import BaseModel

class Item(BaseModel):
    name: str
    item_set: str
    ducats: int
    price: int = 0
    sold: int = 0
    vaulted: bool = False
    item_set_price: int = 0
    item_set_sold: int = 0
    items_to_craft: int = 1
    owned: int = 0
    mastered: bool = False
