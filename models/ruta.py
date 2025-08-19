from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from .base import Base

class Ruta(Base):
    __tablename__ = 'rutas'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), nullable=False)
    latitud = Column(Numeric(9, 6), nullable=False)
    longitud = Column(Numeric(9, 6), nullable=False)
    etiqueta = Column(String(255))
    orden = Column(Integer, nullable=False)

    publicacion = relationship("Publicacion", back_populates="rutas")
