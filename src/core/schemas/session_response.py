from pydantic import BaseModel
from typing import Optional

class SessionResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    metadata: Optional[dict] = None