from sqlalchemy import Column, Enum, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .enums import EstadoAmistadEnum

class Amistad(Base):
    __tablename__ = 'amistades'
    id_usuario1 = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    id_usuario2 = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    estado = Column(Enum(EstadoAmistadEnum), nullable=False)
    id_usuario_accion = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('id_usuario1 < id_usuario2', name='chk_user_order'),
    )
