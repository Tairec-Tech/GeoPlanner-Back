from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    texto: str

class CommentResponse(BaseModel):
    id: str
    id_publicacion: str
    id_autor: str
    texto: str
    fecha_creacion: str

    class Config:
        from_attributes = True
