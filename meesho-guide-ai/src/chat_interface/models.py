from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatSession(BaseModel):
    session_id: str
    user_id: str
    messages: List[Message]
    
class ChatResponse(BaseModel):
    response: str
    context: Optional[List[dict]] = None
    suggested_products: Optional[List[dict]] = None
