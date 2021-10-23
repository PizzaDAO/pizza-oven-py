from typing import Any, Optional
from app.models.base import Base

__all__ = ["PizzaOrderData", "PizzaOrder", "OrderPizzaRequest", "OrderPizzaResponse"]


class PizzaOrderData(Base):
    """Information coming from the blockchain for a pizza order"""

    bridge: str = "orderpizzav1"
    """the name of the chainlink bridge, used to resolve the auth tokens"""
    address: str
    """address of blockchain sender"""
    token_id: int  # = 1
    """the token id that is being redeemed. defaults to 1 for now"""
    recipe_id: int  # = 21  # the current index order of the random pie
    """the index of the recipe to make"""
    requestor: str
    """the address of the requestor"""


class PizzaOrder(Base):
    """Information going to the blockchain for a pizza order"""

    address: str
    """the address that will own the pizza"""
    artwork: Any
    """the ipfs hash of the artwork metadata"""
    metadata: str
    """the ipfs hash of the metadata"""
    order: str
    """the ipfs hash of the order"""


class OrderPizzaRequest(Base):
    """A request to order a pizza, coming from a chainlink oracle"""

    id: str
    data: PizzaOrderData
    meta: Optional[Any]
    responseURL: Optional[str]


class OrderPizzaResponse(Base):
    """A response for a pizza order, as the chainlink oracle expects"""

    jobRunID: str
    data: Any = {}
    error: Optional[str] = None
    pending: bool = False
