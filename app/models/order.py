from app.models.base import Base


class PizzaOrderData(Base):
    """Information coming from the blockchain for a pizza order"""

    address: str
    """address of blockchain sender"""


class PizzaOrder(Base):
    """Information going to the blockchain for a pizza order"""

    address: str
    artwork: str
