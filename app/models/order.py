from typing import Any
from app.models.base import Base


class PizzaOrderData(Base):
    """Information coming from the blockchain for a pizza order"""

    address: str
    """address of blockchain sender"""
    token_id: int = 1
    """the token id that is being redeemed. defaults to 1 for now"""
    recipe_index: int = 21  # the current index order of the random pie
    """the index of the recipe to make"""


class PizzaOrder(Base):
    """Information going to the blockchain for a pizza order"""

    address: str
    """the address that will own the pizza"""
    artwork: Any
    """the ipfs hash of the artwork metadata"""
    metadata: str
    """the ipfs hash of the metadata"""
    recipe: str
    """the ipfs hash of the recipe"""
    order: str
    """the ipfs hash of the order"""
