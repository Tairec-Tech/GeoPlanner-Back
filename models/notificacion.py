from sqlalchemy import Column, Text, ForeignKey, TIMESTAMP, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base

class Notificacion(Base):
    __tablename__ = 'notificaciones'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario_destino = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    id_usuario_origen = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), nullable=True)
    id_comentario = Column(UUID(as_uuid=True), ForeignKey('comentarios.id', ondelete='CASCADE'), nullable=True)
    tipo = Column(String(50), nullable=False)  # 'mencion', 'respuesta', 'like', etc.
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    usuario_destino = relationship("Usuario", foreign_keys=[id_usuario_destino], back_populates="notificaciones_recibidas")
    usuario_origen = relationship("Usuario", foreign_keys=[id_usuario_origen])
    publicacion = relationship("Publicacion")
    comentario = relationship("Comentario")
