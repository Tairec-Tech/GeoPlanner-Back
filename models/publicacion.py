from sqlalchemy import Column, Text, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base
from .enums import TipoPublicacionEnum, TipoPrivacidadEnum, EstadoPublicacionEnum

class Publicacion(Base):
    __tablename__ = 'publicaciones'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_autor = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    texto = Column(Text, nullable=False)
    tipo = Column(Enum(TipoPublicacionEnum), nullable=False)
    fecha_evento = Column(TIMESTAMP(timezone=True), nullable=False)
    privacidad = Column(Enum(TipoPrivacidadEnum), nullable=False, default=TipoPrivacidadEnum.publica)
    media_url = Column(Text)
    terminos_adicionales = Column(Text)
    estado = Column(Enum(EstadoPublicacionEnum), nullable=False, default=EstadoPublicacionEnum.vigente)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    autor = relationship("Usuario", back_populates="publicaciones")
    rutas = relationship("Ruta", back_populates="publicacion", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="publicacion", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="publicacion", cascade="all, delete-orphan")
    inscripciones = relationship("Inscripcion", back_populates="publicacion", cascade="all, delete-orphan")
    guardado_por = relationship("EventoGuardado", back_populates="publicacion", cascade="all, delete-orphan")
