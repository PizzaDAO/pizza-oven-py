from app.models.base import Base

__all__ = ["ChainlinkToken"]

CHAINLINK_AUTH_TOKEN = str
"this is the outgoing token in the chainlink node"
CHAINLINK_RESPONSE_TOKEN = str
"this is the incoming token in the chainlink node"

# Job tokens are required to communicate with the chainlink node
# the chainlink node web interface shows these tokens when you create a bridge.
# you need to put your token in the database at runtime
# or you need to change the defaults below to your values


class ChainlinkToken(Base):
    """the chainlink inbound and outbound tokens"""

    name: str = "orderpizzav1"
    inbound_token: CHAINLINK_AUTH_TOKEN = "Bearer nqpw1bzD4isqeYfXCixyAbhpLs/lkim4"
    outbound_token: CHAINLINK_RESPONSE_TOKEN = "SI/8gEsllRRJLD5HDHH1/2ESG1RKmCOy"
