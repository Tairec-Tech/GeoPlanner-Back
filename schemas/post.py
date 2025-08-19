from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class PostCreate(BaseModel):
    texto: str
    tipo: str
    fecha_evento: datetime
    privacidad: str = "publica"
    media_url: Optional[str] = None
    terminos_adicionales: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    id_autor: str
    texto: str
    tipo: str
    fecha_evento: datetime
    privacidad: str
    media_url: Optional[str]
    terminos_adicionales: Optional[str]
    estado: str
    fecha_creacion: datetime

    class Config:
        orm_mode = True
