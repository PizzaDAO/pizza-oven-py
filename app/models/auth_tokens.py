from typing import Optional, Sequence

from app.models.base import Base
from datetime import datetime

__all__ = ["ChainlinkToken", "GSheetsToken"]

CHAINLINK_AUTH_TOKEN = str
"this is the outgoing token in the chainlink node"
CHAINLINK_RESPONSE_TOKEN = str
"this is the incoming token in the chainlink node"

# Job tokens are required to communicate with the chainlink node
# the chainlink node web interface shows these tokens when you create a bridge.
# you need to put your token in the database at runtime
# or you need to change the defaults below to your values


class GSheetsToken(Base):
    """the auth token for the google sheets"""

    token: Optional[str] = None
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: Sequence[str]
    expiry: datetime


class ChainlinkToken(Base):
    """the chainlink inbound and outbound tokens"""

    name: str = "orderpizzav1"
    outbound_token: CHAINLINK_AUTH_TOKEN = "Bearer nqpw1bzD4isqeYfXCixyAbhpLs/lkim4"
    """
    this is the outbound token from the chainlink node. 
    (from the perspective of the api, it is actually the inbound token. confusing. i know.
    this is the token we receive when a request comes in.
    """
    inbound_token: CHAINLINK_RESPONSE_TOKEN = "SI/8gEsllRRJLD5HDHH1/2ESG1RKmCOy"
    """
    this is the inbound token from the chainlink node. 
    (from the perspective of the api, it is actually the outbound token. confusing. i know.
    this is the token we send out when patching back to a running job.
    """
