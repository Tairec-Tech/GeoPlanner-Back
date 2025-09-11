import enum
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

# Base declarativa para los modelos
Base = declarative_base()

# --- Definición de ENUMs (replicando los de PostgreSQL) ---
# Aunque SQLAlchemy puede manejar los ENUMs de PG, definirlos aquí
# ayuda a la claridad en el código Python.

class TipoGeneroEnum(enum.Enum):
    Masculino = 'Masculino'
    Femenino = 'Femenino'
    Otro = 'Otro'

class TipoPublicacionEnum(enum.Enum):
    Deporte = 'Deporte'
    Social = 'Social'
    Estudio = 'Estudio'
    Cultural = 'Cultural'
    Otro = 'Otro'

class TipoPrivacidadEnum(enum.Enum):
    publica = 'publica'
    amigos = 'amigos'
    privada = 'privada'

class EstadoPublicacionEnum(enum.Enum):
    vigente = 'vigente'
    finalizado = 'finalizado'
    cancelado = 'cancelado'

class EstadoAsistenciaEnum(enum.Enum):
    inscrito = 'inscrito'
    asistio = 'asistio'
    no_asistio = 'no_asistio'

class EstadoVerificacionQREnum(enum.Enum):
    pendiente = 'pendiente'
    verificado = 'verificado'
    cancelado = 'cancelado'

class EstadoAmistadEnum(enum.Enum):
    pendiente = 'pendiente'
    aceptada = 'aceptada'
    rechazada = 'rechazada'
    bloqueada = 'bloqueada'


# --- Definición de Modelos (Tablas) ---

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

    # Relaciones (para que SQLAlchemy pueda hacer JOINs automáticamente)
    publicaciones = relationship("Publicacion", back_populates="autor", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="autor", cascade="all, delete-orphan")
    likes_dados = relationship("Like", back_populates="usuario", cascade="all, delete-orphan")
    inscripciones = relationship("Inscripcion", back_populates="usuario", cascade="all, delete-orphan")
    eventos_guardados = relationship("EventoGuardado", back_populates="usuario", cascade="all, delete-orphan")
    agenda_personal = relationship("ActividadAgenda", back_populates="usuario", cascade="all, delete-orphan")
    notificaciones_recibidas = relationship("Notificacion", foreign_keys="Notificacion.id_usuario_destino", cascade="all, delete-orphan")


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

    # Relaciones
    autor = relationship("Usuario", back_populates="publicaciones")
    rutas = relationship("Ruta", back_populates="publicacion", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="publicacion", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="publicacion", cascade="all, delete-orphan")
    inscripciones = relationship("Inscripcion", back_populates="publicacion", cascade="all, delete-orphan")
    guardado_por = relationship("EventoGuardado", back_populates="publicacion", cascade="all, delete-orphan")


class Ruta(Base):
    __tablename__ = 'rutas'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), nullable=False)
    latitud = Column(Numeric(9, 6), nullable=False)
    longitud = Column(Numeric(9, 6), nullable=False)
    etiqueta = Column(String(255))
    orden = Column(Integer, nullable=False)

    # Relación
    publicacion = relationship("Publicacion", back_populates="rutas")


class Comentario(Base):
    __tablename__ = 'comentarios'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), nullable=False)
    id_autor = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    texto = Column(Text, nullable=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relaciones
    publicacion = relationship("Publicacion", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")


class Like(Base):
    __tablename__ = 'likes'

    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), primary_key=True)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="likes_dados")
    publicacion = relationship("Publicacion", back_populates="likes")


class Inscripcion(Base):
    __tablename__ = 'inscripciones'

    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), primary_key=True)
    fecha_inscripcion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado_asistencia = Column(Enum(EstadoAsistenciaEnum), nullable=False, default=EstadoAsistenciaEnum.inscrito)

    # Relaciones
    usuario = relationship("Usuario", back_populates="inscripciones")
    publicacion = relationship("Publicacion", back_populates="inscripciones")


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


class EventoGuardado(Base):
    __tablename__ = 'eventosguardados'

    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), primary_key=True)
    fecha_guardado = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="eventos_guardados")
    publicacion = relationship("Publicacion", back_populates="guardado_por")


class ActividadAgenda(Base):
    __tablename__ = 'actividadesagenda'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text)
    fecha_actividad = Column(TIMESTAMP(timezone=True), nullable=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relación
    usuario = relationship("Usuario", back_populates="agenda_personal")


class HistorialAsistencia(Base):
    __tablename__ = 'historialasistencia'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_inscripcion_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    id_inscripcion_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), nullable=False)
    id_verificador = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    codigo_qr_data = Column(Text, nullable=False)  # Datos del QR generado
    estado_verificacion = Column(Enum(EstadoVerificacionQREnum), nullable=False, default=EstadoVerificacionQREnum.pendiente)
    fecha_verificacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ubicacion_verificacion_lat = Column(Numeric(9, 6))  # Ubicación donde se escaneó
    ubicacion_verificacion_lng = Column(Numeric(9, 6))
    notas_verificacion = Column(Text)  # Notas adicionales del verificador
    
    # Relaciones
    inscripcion_usuario = relationship("Usuario", foreign_keys=[id_inscripcion_usuario])
    inscripcion_publicacion = relationship("Publicacion", foreign_keys=[id_inscripcion_publicacion])
    verificador = relationship("Usuario", foreign_keys=[id_verificador])


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

    # Relaciones
    usuario_destino = relationship("Usuario", foreign_keys=[id_usuario_destino], back_populates="notificaciones_recibidas")
    usuario_origen = relationship("Usuario", foreign_keys=[id_usuario_origen])
    publicacion = relationship("Publicacion")
    comentario = relationship("Comentario")
