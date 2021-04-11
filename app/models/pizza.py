from typing import Any, Dict, List, Optional

from .base import Base


__all__ = [
    "HotPizza",
]

ASSET_KEY = str


class HotPizza(Base):
    """The rendered pizza object that includes all metadata and routes
    and everything necessary to seed IPFS and the blockchain"""

    unique_id: int
    order_id: int
    recipe_id: int
    assets: Dict[ASSET_KEY, str]
