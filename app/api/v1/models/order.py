from dataclasses import dataclass
from typing import Dict, List, NamedTuple

from .base import Base


@dataclass
class PizzaData:
    address: str


class PizzaOrder(Base):
    address: str
    artwork: str


class OrderPizzaRequest(Base):
    """A request to order a pizza, coming from a chainlink oracle"""

    id: str
    data: PizzaData


class OrderPizzaResponse(Base):
    """A response for a pizza order, as the chainlink oracle expects"""

    jobRunID: str
    data: PizzaOrder
    statusCode: int = 200


def sample(request: OrderPizzaRequest) -> OrderPizzaResponse:
    """just a sample"""

    return OrderPizzaResponse(
        jobRunID=request.id,
        data=PizzaOrder(
            address=request.data.address,
            artwork="QmZ4q72eVU3bX95GXwMXLrguybKLKavmStLWEWVJZ1jeyz",
        ),
    )
