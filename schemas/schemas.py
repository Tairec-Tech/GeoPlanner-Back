from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

# Importar los Enums de los modelos para mantener consistencia
from models.models import (
    TipoGeneroEnum,
    TipoPublicacionEnum,
    TipoPrivacidadEnum,
    EstadoPublicacionEnum,
    EstadoAsistenciaEnum,
    EstadoAmistadEnum,
    
)

# =============================================================================
# ESQUEMAS PARA USUARIOS
# =============================================================================

# Esquema base para un usuario, con campos compartidos
class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)

# Esquema para la creación de un nuevo usuario
class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)
    fecha_nacimiento: date
    genero: Optional[TipoGeneroEnum] = None
    foto_perfil_url: Optional[str] = None
    biografia: Optional[str] = Field(None, max_length=160)
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tema_preferido: Optional[str] = 'default'

# Esquema para la respuesta de la API (nunca debe incluir la contraseña)
class Usuario(UsuarioBase):
    id: UUID
    verificado: bool
    fecha_creacion: datetime
    foto_perfil_url: Optional[str] = None
    biografia: Optional[str] = None
    tema_preferido: str

    class Config:
        orm_mode = True # Permite que Pydantic lea datos desde modelos ORM

# =============================================================================
# ESQUEMAS PARA PUBLICACIONES Y RUTAS
# =============================================================================

# Esquema para un punto de una ruta
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

# Esquema base para una publicación
class PublicacionBase(BaseModel):
    texto: str
    tipo: TipoPublicacionEnum
    fecha_evento: datetime
    privacidad: TipoPrivacidadEnum = TipoPrivacidadEnum.publica
    media_url: Optional[str] = None
    terminos_adicionales: Optional[str] = None

# Esquema para crear una publicación (incluye las rutas)
class PublicacionCreate(PublicacionBase):
    rutas: List[RutaCreate]

# Esquema completo para mostrar una publicación (incluye datos del autor y rutas)
class Publicacion(PublicacionBase):
    id: UUID
    id_autor: UUID
    estado: EstadoPublicacionEnum
    fecha_creacion: datetime
    autor: Usuario # Anidamos el esquema del autor para mostrar su info
    rutas: List[Ruta] = []

    class Config:
        orm_mode = True

# =============================================================================
# ESQUEMAS PARA AUTENTICACIÓN
# =============================================================================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    nombre_usuario: Optional[str] = None

# =============================================================================
# ESQUEMAS PARA OTRAS ENTIDADES (Comentarios, Likes, etc.)
# =============================================================================

# --- Comentarios ---
class ComentarioBase(BaseModel):
    texto: str

class ComentarioCreate(ComentarioBase):
    id_publicacion: UUID

class Comentario(ComentarioBase):
    id: UUID
    id_publicacion: UUID
    id_autor: UUID
    fecha_creacion: datetime
    autor: Usuario # Anidamos para mostrar quién comentó

    class Config:
        orm_mode = True

# --- Agenda ---
class ActividadAgendaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_actividad: datetime

class ActividadAgendaCreate(ActividadAgendaBase):
    pass

class ActividadAgenda(ActividadAgendaBase):
    id: UUID
    id_usuario: UUID
    fecha_creacion: datetime

    class Config:
        orm_mode = True
