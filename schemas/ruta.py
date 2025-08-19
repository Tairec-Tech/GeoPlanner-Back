from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RutaBase(BaseModel):
    latitud: float
    longitud: float
    etiqueta: Optional[str] = None
    orden: int

class RutaCreate(RutaBase):
    pass

class Ruta(RutaBase):
    id: UUID
    id_publicacion: UUID

    class Config:
        orm_mode = True
