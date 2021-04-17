from typing import Any, Dict, List, Optional, Union

from .base import Base
from .recipe import NutritionMetadata


__all__ = ["HotPizza", "RarePizzaMetadata"]

ASSET_KEY = str


class ERC721OpenSeaMetadataAttribute(Base):
    trait_type: str
    value: Union[str, int]


class ERC721Metadata(Base):
    name: str
    """Name of the item."""
    description: str
    """A human readable description of the item. Markdown is supported."""
    image: str
    """This is the URL to the image of the item."""


class ERC721OpenSeaExtensions(Base):
    """
    https://docs.opensea.io/docs/metadata-standards
    """

    external_url: str
    """This is the URL that will appear below the asset's image on OpenSea and view the item on your site."""
    background_color: str
    """Background color of the item on OpenSea. Must be a six-character hexadecimal without a pre-pended #."""
    attributes: List[ERC721OpenSeaMetadataAttribute]
    """These are the attributes for the item, which will show up on the OpenSea page for the item."""


class IngredientMetadata(Base):
    name: str
    rarity: int
    classification: str
    category: str
    attributes: List[ERC721OpenSeaMetadataAttribute]
    nutrition: NutritionMetadata


class RarePizzaMetadata(ERC721Metadata, ERC721OpenSeaExtensions):
    order_id: str
    """the order job id"""
    rarity_level: int
    random_seed: str
    extension_uri: str
    """a uri that we can predefine and add content to later"""
    baking_temp_in_celsius: int
    baking_time_in_minutes: int
    ingredients: List[IngredientMetadata]


class HotPizza(Base):
    """The rendered pizza object that includes all metadata and routes
    and everything necessary to seed IPFS and the blockchain"""

    unique_id: int
    order_id: int
    recipe_id: int
    assets: Dict[ASSET_KEY, str]
