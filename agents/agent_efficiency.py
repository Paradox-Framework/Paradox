from typing import Optional, Type
from pydantic import BaseModel
import datetime
import json

class WalletSignal(BaseModel):
    wallet_id: str
    last_txn: Optional[datetime.datetime] = None
    is_flagged: bool = False

def has_recent_activity(signal: WalletSignal) -> bool:
    return signal.last_txn is not None

def export_signal_schema(model: Type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema(), indent=4)
