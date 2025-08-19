from sqlalchemy import Column, String, Text, Boolean, Date, Enum, Numeric, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base
from .enums import TipoGeneroEnum

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_usuario = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(Enum(TipoGeneroEnum))
    foto_perfil_url = Column(Text)
    biografia = Column(String(160))
    latitud = Column(Numeric(9, 6))
    longitud = Column(Numeric(9, 6))
    ciudad = Column(String(100))
    pais = Column(String(100))
    tema_preferido = Column(String(50), default='default')
    verificado = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    publicaciones = relationship("Publicacion", back_populates="autor", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="autor", cascade="all, delete-orphan")
    likes_dados = relationship("Like", back_populates="usuario", cascade="all, delete-orphan")
    inscripciones = relationship("Inscripcion", back_populates="usuario", cascade="all, delete-orphan")
    eventos_guardados = relationship("EventoGuardado", back_populates="usuario", cascade="all, delete-orphan")
    agenda_personal = relationship("ActividadAgenda", back_populates="usuario", cascade="all, delete-orphan")
    notificaciones_recibidas = relationship("Notificacion", foreign_keys="Notificacion.id_usuario_destino", back_populates="usuario_destino", cascade="all, delete-orphan")
