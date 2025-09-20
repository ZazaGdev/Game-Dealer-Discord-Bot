# models/deals.py
from typing import TypedDict, Optional

class Deal(TypedDict, total=False):
    title: str
    price: str
    store: str
    url: str
    discount: Optional[str]
    original_price: Optional[str]
