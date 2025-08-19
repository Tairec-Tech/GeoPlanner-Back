from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Like(Base):
    __tablename__ = 'likes'
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), primary_key=True)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="likes_dados")
    publicacion = relationship("Publicacion", back_populates="likes")
