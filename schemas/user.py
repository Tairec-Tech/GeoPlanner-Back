from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    fecha_nacimiento: date
    # ...otros campos opcionales...

class Usuario(UsuarioBase):
    id: UUID
    verificado: bool
    fecha_creacion: datetime
    # ...otros campos opcionales...

    class Config:
        from_attributes = True
