from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base

class ConfiguracionUsuario(Base):
    __tablename__ = 'configuraciones_usuario'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Notificaciones
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    new_friend_requests = Column(Boolean, default=True)
    event_invitations = Column(Boolean, default=True)
    likes_and_comments = Column(Boolean, default=True)
    mentions = Column(Boolean, default=True)
    nearby_events = Column(Boolean, default=False)
    weekly_digest = Column(Boolean, default=True)
    
    # Privacidad
    profile_visibility = Column(String(20), default='public')  # public, friends, private
    show_location = Column(Boolean, default=True)
    show_birth_date = Column(Boolean, default=True)
    allow_friend_requests = Column(Boolean, default=True)
    allow_messages = Column(Boolean, default=True)
    show_online_status = Column(Boolean, default=True)
    allow_tagging = Column(Boolean, default=True)
    
    # Seguridad
    two_factor_auth = Column(Boolean, default=False)
    login_alerts = Column(Boolean, default=True)
    device_management = Column(Boolean, default=True)
    
    # Contenido
    language = Column(String(10), default='es')
    timezone = Column(String(50), default='America/Caracas')
    content_filter = Column(String(20), default='moderate')  # none, moderate, strict
    auto_play_videos = Column(Boolean, default=True)
    show_trending_content = Column(Boolean, default=True)
    
    # Datos
    data_usage = Column(String(20), default='standard')  # standard, reduced
    analytics_sharing = Column(Boolean, default=True)
    personalized_ads = Column(Boolean, default=False)
    
    # Metadatos
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="configuracion")
    
    def to_dict(self):
        """Convierte la configuración a un diccionario"""
        return {
            "id": str(self.id),
            "id_usuario": str(self.id_usuario),
            
            # Notificaciones
            "emailNotifications": self.email_notifications,
            "pushNotifications": self.push_notifications,
            "newFriendRequests": self.new_friend_requests,
            "eventInvitations": self.event_invitations,
            "likesAndComments": self.likes_and_comments,
            "mentions": self.mentions,
            "nearbyEvents": self.nearby_events,
            "weeklyDigest": self.weekly_digest,
            
            # Privacidad
            "profileVisibility": self.profile_visibility,
            "showLocation": self.show_location,
            "showBirthDate": self.show_birth_date,
            "allowFriendRequests": self.allow_friend_requests,
            "allowMessages": self.allow_messages,
            "showOnlineStatus": self.show_online_status,
            "allowTagging": self.allow_tagging,
            
            # Seguridad
            "twoFactorAuth": self.two_factor_auth,
            "loginAlerts": self.login_alerts,
            "deviceManagement": self.device_management,
            
            # Contenido
            "language": self.language,
            "timezone": self.timezone,
            "contentFilter": self.content_filter,
            "autoPlayVideos": self.auto_play_videos,
            "showTrendingContent": self.show_trending_content,
            
            # Datos
            "dataUsage": self.data_usage,
            "analyticsSharing": self.analytics_sharing,
            "personalizedAds": self.personalized_ads,
            
            # Metadatos
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
