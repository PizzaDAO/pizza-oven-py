from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .base import Base

from .prep import KitchenOrder

__all__ = [
    "HotPizza",
    "HotPizzaResponse",
]

ASSET_KEY = str


@dataclass
class HotPizza:
    """The rendered pizza object that includes all metadata and routes
    and everything necessary to seed IPFS and the blockchain"""

    unique_id: int
    order_id: int
    recipe_id: int
    assets: Dict[ASSET_KEY, str]


class HotPizzaResponse(Base):
    """a made pizza response"""

    pizza: HotPizza


def sample(order: KitchenOrder) -> HotPizza:
    """just a sample"""
    return HotPizza(
        unique_id=12345, order_id=order.unique_id, recipe_id=order.recipe_id, assets={}
    )
