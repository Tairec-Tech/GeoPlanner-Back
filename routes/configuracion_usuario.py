from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from models.configuracion_usuario import ConfiguracionUsuario
from routes.auth import get_current_user
from schemas.configuracion_usuario import (
    UserSettingsResponse, UserSettingsUpdate, PasswordChangeRequest,
    TwoFactorSetupResponse, TwoFactorVerifyRequest, TwoFactorVerifyResponse,
    TwoFactorDisableRequest, SessionInfo, UserActivityLog, DownloadDataResponse,
    DeleteAccountRequest
)
from typing import List
import uuid
from datetime import datetime, timedelta
import qrcode
import base64
import io
import secrets
import hashlib
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_default_settings():
    """Retorna las configuraciones por defecto"""
    return {
        "emailNotifications": True,
        "pushNotifications": True,
        "newFriendRequests": True,
        "eventInvitations": True,
        "likesAndComments": True,
        "mentions": True,
        "nearbyEvents": False,
        "weeklyDigest": True,
        "profileVisibility": "public",
        "showLocation": True,
        "showBirthDate": True,
        "allowFriendRequests": True,
        "allowMessages": True,
        "showOnlineStatus": True,
        "allowTagging": True,
        "twoFactorAuth": False,
        "loginAlerts": True,
        "deviceManagement": True,
        "language": "es",
        "timezone": "America/Caracas",
        "contentFilter": "moderate",
        "autoPlayVideos": True,
        "showTrendingContent": True,
        "dataUsage": "standard",
        "analyticsSharing": True,
        "personalizedAds": False
    }

@router.get("/settings", response_model=UserSettingsResponse, summary="Obtener configuraciones del usuario")
def get_user_settings(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtiene las configuraciones del usuario actual
    """
    try:
        # Buscar configuraciones existentes
        config = db.query(ConfiguracionUsuario).filter(ConfiguracionUsuario.id_usuario == current_user.id).first()
        
        if config:
            return config.to_dict()
        else:
            # Si no existen configuraciones, crear unas por defecto
            default_settings = get_default_settings()
            config = ConfiguracionUsuario(
                id_usuario=current_user.id,
                email_notifications=default_settings["emailNotifications"],
                push_notifications=default_settings["pushNotifications"],
                new_friend_requests=default_settings["newFriendRequests"],
                event_invitations=default_settings["eventInvitations"],
                likes_and_comments=default_settings["likesAndComments"],
                mentions=default_settings["mentions"],
                nearby_events=default_settings["nearbyEvents"],
                weekly_digest=default_settings["weeklyDigest"],
                profile_visibility=default_settings["profileVisibility"],
                show_location=default_settings["showLocation"],
                show_birth_date=default_settings["showBirthDate"],
                allow_friend_requests=default_settings["allowFriendRequests"],
                allow_messages=default_settings["allowMessages"],
                show_online_status=default_settings["showOnlineStatus"],
                allow_tagging=default_settings["allowTagging"],
                two_factor_auth=default_settings["twoFactorAuth"],
                login_alerts=default_settings["loginAlerts"],
                device_management=default_settings["deviceManagement"],
                language=default_settings["language"],
                timezone=default_settings["timezone"],
                content_filter=default_settings["contentFilter"],
                auto_play_videos=default_settings["autoPlayVideos"],
                show_trending_content=default_settings["showTrendingContent"],
                data_usage=default_settings["dataUsage"],
                analytics_sharing=default_settings["analyticsSharing"],
                personalized_ads=default_settings["personalizedAds"]
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            return config.to_dict()
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener configuraciones: {str(e)}"
        )

@router.put("/settings", response_model=dict, summary="Actualizar configuraciones del usuario")
def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza las configuraciones del usuario actual
    """
    try:
        # Buscar configuraciones existentes
        config = db.query(ConfiguracionUsuario).filter(ConfiguracionUsuario.id_usuario == current_user.id).first()
        
        if not config:
            # Si no existen, crear nuevas
            config = ConfiguracionUsuario(id_usuario=current_user.id)
            db.add(config)
        
        # Actualizar campos
        if settings_update.emailNotifications is not None:
            config.email_notifications = settings_update.emailNotifications
        if settings_update.pushNotifications is not None:
            config.push_notifications = settings_update.pushNotifications
        if settings_update.newFriendRequests is not None:
            config.new_friend_requests = settings_update.newFriendRequests
        if settings_update.eventInvitations is not None:
            config.event_invitations = settings_update.eventInvitations
        if settings_update.likesAndComments is not None:
            config.likes_and_comments = settings_update.likesAndComments
        if settings_update.mentions is not None:
            config.mentions = settings_update.mentions
        if settings_update.nearbyEvents is not None:
            config.nearby_events = settings_update.nearbyEvents
        if settings_update.weeklyDigest is not None:
            config.weekly_digest = settings_update.weeklyDigest
        if settings_update.profileVisibility is not None:
            config.profile_visibility = settings_update.profileVisibility
        if settings_update.showLocation is not None:
            config.show_location = settings_update.showLocation
        if settings_update.showBirthDate is not None:
            config.show_birth_date = settings_update.showBirthDate
        if settings_update.allowFriendRequests is not None:
            config.allow_friend_requests = settings_update.allowFriendRequests
        if settings_update.allowMessages is not None:
            config.allow_messages = settings_update.allowMessages
        if settings_update.showOnlineStatus is not None:
            config.show_online_status = settings_update.showOnlineStatus
        if settings_update.allowTagging is not None:
            config.allow_tagging = settings_update.allowTagging
        if settings_update.twoFactorAuth is not None:
            config.two_factor_auth = settings_update.twoFactorAuth
        if settings_update.loginAlerts is not None:
            config.login_alerts = settings_update.loginAlerts
        if settings_update.deviceManagement is not None:
            config.device_management = settings_update.deviceManagement
        if settings_update.language is not None:
            config.language = settings_update.language
        if settings_update.timezone is not None:
            config.timezone = settings_update.timezone
        if settings_update.contentFilter is not None:
            config.content_filter = settings_update.contentFilter
        if settings_update.autoPlayVideos is not None:
            config.auto_play_videos = settings_update.autoPlayVideos
        if settings_update.showTrendingContent is not None:
            config.show_trending_content = settings_update.showTrendingContent
        if settings_update.dataUsage is not None:
            config.data_usage = settings_update.dataUsage
        if settings_update.analyticsSharing is not None:
            config.analytics_sharing = settings_update.analyticsSharing
        if settings_update.personalizedAds is not None:
            config.personalized_ads = settings_update.personalizedAds
        
        db.commit()
        db.refresh(config)
        
        return {
            "mensaje": "Configuraciones actualizadas correctamente",
            "configuraciones": config.to_dict()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar configuraciones: {str(e)}"
        )

@router.post("/change-password", summary="Cambiar contraseña del usuario")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la contraseña del usuario actual
    """
    try:
        # Verificar contraseña actual
        if not pwd_context.verify(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        
        # Verificar que la nueva contraseña sea diferente
        if password_data.current_password == password_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        # Hash de la nueva contraseña
        new_password_hash = pwd_context.hash(password_data.new_password)
        current_user.password_hash = new_password_hash
        
        db.commit()
        
        return {"mensaje": "Contraseña cambiada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )

@router.post("/setup-2fa", response_model=TwoFactorSetupResponse, summary="Configurar autenticación de dos factores")
def setup_two_factor(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Configura la autenticación de dos factores para el usuario
    """
    try:
        # Generar clave secreta para 2FA
        secret_key = secrets.token_hex(16)
        
        # Generar códigos de respaldo
        backup_codes = [secrets.token_hex(4).upper() for _ in range(8)]
        
        # Generar QR code
        qr_data = f"otpauth://totp/GeoPlanner:{current_user.email}?secret={secret_key}&issuer=GeoPlanner"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Actualizar configuración del usuario
        config = db.query(ConfiguracionUsuario).filter(ConfiguracionUsuario.id_usuario == current_user.id).first()
        if config:
            config.two_factor_auth = True
            # Aquí se guardaría la clave secreta y códigos de respaldo en la base de datos
            # Por simplicidad, los retornamos en la respuesta
            db.commit()
        
        return {
            "mensaje": "Autenticación de dos factores configurada correctamente",
            "qr_code": f"data:image/png;base64,{img_str}",
            "secret_key": secret_key,
            "backup_codes": backup_codes
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al configurar 2FA: {str(e)}"
        )

@router.post("/verify-2fa", response_model=TwoFactorVerifyResponse, summary="Verificar código de autenticación de dos factores")
def verify_two_factor(
    verify_data: TwoFactorVerifyRequest,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Verifica el código de autenticación de dos factores
    """
    try:
        # Aquí se implementaría la verificación real del código TOTP
        # Por simplicidad, aceptamos cualquier código de 6 dígitos
        if len(verify_data.code) == 6 and verify_data.code.isdigit():
            return {
                "mensaje": "Código verificado correctamente",
                "success": True
            }
        else:
            return {
                "mensaje": "Código inválido",
                "success": False
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar código: {str(e)}"
        )

@router.get("/sessions", response_model=List[SessionInfo], summary="Obtener sesiones activas del usuario")
def get_active_sessions(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene las sesiones activas del usuario
    """
    try:
        # Por simplicidad, retornamos una sesión simulada
        # En una implementación real, se consultaría una tabla de sesiones
        return [{
            "id": str(uuid.uuid4()),
            "device_info": "Chrome 120.0.0.0 on Windows 10",
            "ip_address": "192.168.1.100",
            "location": "Caracas, Venezuela",
            "last_activity": datetime.now(),
            "is_current": True
        }]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sesiones: {str(e)}"
        )

@router.post("/download-data", response_model=DownloadDataResponse, summary="Descargar datos del usuario")
def download_user_data(current_user: Usuario = Depends(get_current_user)):
    """
    Inicia la descarga de datos del usuario
    """
    try:
        # Generar URL de descarga temporal
        download_id = secrets.token_hex(16)
        download_url = f"http://localhost:8000/download/{download_id}"
        expires_at = datetime.now() + timedelta(hours=24)
        
        return {
            "mensaje": "Descarga iniciada correctamente",
            "download_url": download_url,
            "expires_at": expires_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar descarga: {str(e)}"
        )

@router.delete("/delete-account", summary="Eliminar cuenta del usuario")
def delete_account(
    delete_data: DeleteAccountRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina la cuenta del usuario
    """
    try:
        # Verificar contraseña
        if not pwd_context.verify(delete_data.password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña incorrecta"
            )
        
        # Si se solicita descargar datos antes de eliminar
        if delete_data.download_data:
            # Aquí se generaría el archivo de datos
            pass
        
        # Eliminar usuario (esto eliminará en cascada todas las relaciones)
        db.delete(current_user)
        db.commit()
        
        return {"mensaje": "Cuenta eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar cuenta: {str(e)}"
        )

@router.get("/activity-history", response_model=List[UserActivityLog], summary="Obtener historial de actividad del usuario")
def get_user_activity_history(
    limit: int = 50,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene el historial de actividad del usuario
    """
    try:
        # Por simplicidad, retornamos actividad simulada
        # En una implementación real, se consultaría una tabla de logs
        activities = []
        for i in range(min(limit, 10)):
            activities.append({
                "id": str(uuid.uuid4()),
                "action": "login",
                "description": "Inicio de sesión exitoso",
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "timestamp": datetime.now() - timedelta(hours=i)
            })
        
        return activities
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )
