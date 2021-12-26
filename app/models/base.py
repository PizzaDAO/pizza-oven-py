from typing import Any, Optional
from pydantic import BaseModel

__all__ = ["Base", "BaseQueryRequest"]


class Base(BaseModel):
    pass


class BaseQueryRequest(Base):
    """Find something"""

    filter: Optional[Any] = None
