from dataclasses import dataclass
from datetime import datetime


@dataclass
class Record:
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
