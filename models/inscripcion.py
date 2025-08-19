from sqlalchemy import Column, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .enums import EstadoAsistenciaEnum

class Inscripcion(Base):
    __tablename__ = 'inscripciones'
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), primary_key=True)
    fecha_inscripcion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado_asistencia = Column(Enum(EstadoAsistenciaEnum), nullable=False, default=EstadoAsistenciaEnum.inscrito)

    usuario = relationship("Usuario", back_populates="inscripciones")
    publicacion = relationship("Publicacion", back_populates="inscripciones")
