from sqlalchemy import Column, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
# backref ha sido importado aquí
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import uuid
import re
from .base import Base

class Comentario(Base):
    __tablename__ = 'comentarios'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id', ondelete='CASCADE'), nullable=False)
    id_autor = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    id_comentario_padre = Column(UUID(as_uuid=True), ForeignKey('comentarios.id', ondelete='CASCADE'), nullable=True)
    texto = Column(Text, nullable=False)
    menciones = Column(Text, nullable=True)  # JSON string con lista de usernames mencionados
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())

    publicacion = relationship("Publicacion", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")

    # --- LÍNEA CORREGIDA ---
    # Se movió `remote_side=[id]` dentro de la función `backref`.
    # Esto le indica a SQLAlchemy que la relación 'padre' es la que apunta al
    # lado "remoto" (el comentario original), estableciendo correctamente la
    # relación uno-a-muchos para 'respuestas'.
    respuestas = relationship(
        "Comentario",
        cascade="all, delete-orphan",
        backref=backref("padre", remote_side=[id])
    )
    
    def extraer_menciones(self):
        """Extrae menciones del texto del comentario"""
        if not self.texto:
            return []
        
        # Buscar patrones @username
        menciones = re.findall(r'@(\w+)', self.texto)
        return list(set(menciones))  # Eliminar duplicados
    
    def establecer_menciones(self):
        """Establece las menciones basadas en el texto"""
        menciones = self.extraer_menciones()
        import json
        self.menciones = json.dumps(menciones) if menciones else None
