from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AgendaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_actividad: datetime

class AgendaResponse(BaseModel):
    id: str
    id_usuario: str
    titulo: str
    descripcion: Optional[str]
    fecha_actividad: datetime
    fecha_creacion: datetime

    class Config:
        from_attributes = True
