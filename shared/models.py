from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Dict, Any
import time

class TaskStatus(str, Enum):
    RECEIVED = "received"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    status: TaskStatus
    payload: Dict[str, Any]
    retry_count: int = 0
    result: Optional[Dict[str, Any]] = None
    created_at: int = int(time.time())
    updated_at: int = int(time.time())

    def to_dict(self):
        return asdict(self)
