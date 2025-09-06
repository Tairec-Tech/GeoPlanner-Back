from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserSettingsBase(BaseModel):
    # Notificaciones
    emailNotifications: Optional[bool] = True
    pushNotifications: Optional[bool] = True
    newFriendRequests: Optional[bool] = True
    eventInvitations: Optional[bool] = True
    likesAndComments: Optional[bool] = True
    mentions: Optional[bool] = True
    nearbyEvents: Optional[bool] = False
    weeklyDigest: Optional[bool] = True
    
    # Privacidad
    profileVisibility: Optional[str] = 'public'  # public, friends, private
    showLocation: Optional[bool] = True
    showBirthDate: Optional[bool] = True
    allowFriendRequests: Optional[bool] = True
    allowMessages: Optional[bool] = True
    showOnlineStatus: Optional[bool] = True
    allowTagging: Optional[bool] = True
    
    # Seguridad
    twoFactorAuth: Optional[bool] = False
    loginAlerts: Optional[bool] = True
    deviceManagement: Optional[bool] = True
    
    # Contenido
    language: Optional[str] = 'es'
    timezone: Optional[str] = 'America/Caracas'
    contentFilter: Optional[str] = 'moderate'  # none, moderate, strict
    autoPlayVideos: Optional[bool] = True
    showTrendingContent: Optional[bool] = True
    
    # Datos
    dataUsage: Optional[str] = 'standard'  # standard, reduced
    analyticsSharing: Optional[bool] = True
    personalizedAds: Optional[bool] = False

class UserSettingsResponse(UserSettingsBase):
    id: str
    id_usuario: str
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

class UserSettingsUpdate(UserSettingsBase):
    pass

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class TwoFactorSetupResponse(BaseModel):
    mensaje: str
    qr_code: str
    secret_key: str
    backup_codes: list[str]

class TwoFactorVerifyRequest(BaseModel):
    code: str

class TwoFactorVerifyResponse(BaseModel):
    mensaje: str
    success: bool

class TwoFactorDisableRequest(BaseModel):
    password: str

class SessionInfo(BaseModel):
    id: str
    device_info: str
    ip_address: str
    location: str
    last_activity: datetime
    is_current: bool

class UserActivityLog(BaseModel):
    id: str
    action: str
    description: str
    ip_address: str
    user_agent: str
    timestamp: datetime

class DownloadDataResponse(BaseModel):
    mensaje: str
    download_url: str
    expires_at: datetime

class DeleteAccountRequest(BaseModel):
    reason: Optional[str] = None
    password: str
    download_data: bool = True
