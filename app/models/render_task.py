from typing import Dict, Optional, List, Tuple
from enum import Enum

from datetime import datetime, timedelta, timezone

from app.models.base import Base
from app.models.order import OrderPizzaRequest

__all__ = ["TaskStatus", "RenderTask"]


class TaskStatus(str, Enum):
    new = "new"
    started = "started"
    error = "error"
    complete = "complete"


class RenderTask(Base):
    """a render task that is mutable"""

    job_id: str
    """the job id"""
    request_token: str
    """the authorization request token"""
    request: OrderPizzaRequest
    """the original request passed in"""
    status: TaskStatus = TaskStatus.new

    timestamp: datetime = datetime.now(timezone.utc)
    random_number: Optional[str]
    """the random number in hex returned from chainlink"""
    metadata_hash: Optional[str]
    """the ipfs hash of the metadata when the rendering is complete"""
    truncated_metadata: Optional[str] = None
    """the truncated ipfs hash of the metadata decoded from base-58 and re-encoded in base-16"""
    message: Optional[str] = None

    def set_status(self, new_status: TaskStatus) -> None:
        self.status = new_status
        self.timestamp = datetime.now(timezone.utc)

    def should_restart(self, timeout_in_mins: int = 15) -> bool:
        """job should restart if certain conditions are met"""
        return (
            self.status == TaskStatus.new
            or self.status == TaskStatus.error
            or (
                self.status == TaskStatus.started
                and datetime.now(timezone.utc) - self.timestamp
                > timedelta(minutes=timeout_in_mins)
            )
        )
