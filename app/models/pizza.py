from typing import Dict, List, Union, Optional

from app.models.base import Base
from app.models.recipe import NutritionMetadata


__all__ = ["HotPizza", "RarePizzaMetadata"]

ASSET_KEY = str


class ERC721OpenSeaMetadataAttribute(Base):
    trait_type: str
    value: Union[str, int]


class ERC721OpenSeaMetadataBoostAttribute(Base):
    """For attributes to be displayed on a numeric or percentage scale"""

    display_type: str
    """Should be set to 'boost_number' or 'boost_percentage'"""
    trait_type: str
    value: int
    max_value: Optional[int]
    """Sets a ceiling to the scale, otherwise will be infered by max observer in rest of NFT collection."""


class ERC721Metadata(Base):
    name: str
    """Name of the item."""
    description: str
    """A human readable description of the item. Markdown is supported."""
    image: str
    """This is the URL to the image of the item."""


METADATA_ATTRIBUTE = Union[
    ERC721OpenSeaMetadataBoostAttribute, ERC721OpenSeaMetadataAttribute
]


class ERC721OpenSeaExtensions(Base):
    """
    https://docs.opensea.io/docs/metadata-standards
    """

    external_url: str
    """This is the URL that will appear below the asset's image on OpenSea and view the item on your site."""
    background_color: str
    """Background color of the item on OpenSea. Must be a six-character hexadecimal without a pre-pended #."""
    attributes: List[METADATA_ATTRIBUTE]
    """These are the attributes for the item, which will show up on the OpenSea page for the item."""


class IngredientMetadata(Base):
    """ingreident metadata"""

    # TODO: conform to the ERC721 standard so that ingredentis could also be their own tokens"""

    # TODO: add artist attribution & copyright info
    name: str
    rarity: int
    classification: str
    category: str
    attributes: List[ERC721OpenSeaMetadataAttribute]
    nutrition: NutritionMetadata


class RarePizzaMetadata(ERC721Metadata, ERC721OpenSeaExtensions):
    job_id: str
    """the order job id, usually the chainlink job id"""
    token_id: int
    """the token id of the pizza that was made"""
    rarity_level: int
    random_seed: str
    "the random seed used to create the order"
    extension_uri: str
    """a uri that we can predefine and add content to later"""
    baking_temp_in_celsius: int
    baking_time_in_minutes: int
    ingredients: List[IngredientMetadata]


class HotPizza(Base):
    """The rendered pizza object that includes all metadata and routes
    and everything necessary to seed IPFS and the blockchain"""

    job_id: str
    """the order job id, usually the chainlink job id"""
    token_id: int
    """the token id of the pizza that was made"""
    random_seed: str
    "the random seed used to create the order"
    recipe_id: int
    "the recipe id that was used to create the order"
    assets: Dict[ASSET_KEY, str]
