# rlam/action.py
from typing import Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class Action(BaseModel):
    action_id: str
    action_type: str
    inputs: Dict[str, Any]
    parameters: Dict[str, Any]
    environment_hash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = True
