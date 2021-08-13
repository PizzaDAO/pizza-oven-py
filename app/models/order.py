from app.models.base import Base


class PizzaOrderData(Base):
    """Information coming from the blockchain for a pizza order"""

    address: str
    """address of blockchain sender"""


class PizzaOrder(Base):
    """Information going to the blockchain for a pizza order"""

    address: str
    """the address that will own the pizza"""
    artwork: str
    """the ipfs hash of the artwork metadata"""
    recipe: str
    """the ipfs hash of the recipe"""
    order: str
    """the ipfs hash of the order"""
