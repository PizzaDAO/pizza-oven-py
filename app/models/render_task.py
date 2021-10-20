from typing import Dict, Optional, List, Tuple
from enum import Enum

from datetime import datetime, timedelta

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
    request_token: str
    request: OrderPizzaRequest
    metadata_hash: Optional[str]
    status: TaskStatus = TaskStatus.new
    timestamp: datetime = datetime.utcnow()

    def set_status(self, new_status: TaskStatus) -> None:
        self.status = new_status
        self.timestamp = datetime.utcnow()

    def should_restart(self) -> bool:
        """job should restart if certain conditions are met"""
        return (
            self.status == TaskStatus.new
            or self.status == TaskStatus.error
            or (
                self.status == TaskStatus.started
                and datetime.utcnow() - self.timestamp > timedelta(minutes=15)
            )
        )
