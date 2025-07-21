from pydantic import BaseModel
from datetime import datetime

class AgendaCreate(BaseModel):
    title: str
    description: str
    date: datetime

class AgendaResponse(BaseModel):
    id: int
    title: str
    description: str
    date: datetime
    user_id: int

    class Config:
         from_attributes = True