from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.notificacion import Notificacion
from models.usuario import Usuario
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime

router = APIRouter()

class NotificationResponse(BaseModel):
    id: str
    id_usuario_destino: str
    id_usuario_origen: str
    id_publicacion: str
    id_comentario: str
    tipo: str
    mensaje: str
    leida: bool
    fecha_creacion: str
    nombre_usuario_origen: str
    username_usuario_origen: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

@router.get("/", response_model=List[NotificationResponse], summary="Obtener notificaciones del usuario")
def get_user_notifications(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las notificaciones del usuario actual
    """
    try:
        notifications = db.query(Notificacion).join(
            Usuario, Notificacion.id_usuario_origen == Usuario.id
        ).filter(
            Notificacion.id_usuario_destino == str(current_user.id)
        ).order_by(Notificacion.fecha_creacion.desc()).all()
        
        converted_notifications = []
        for notification in notifications:
            converted_notifications.append({
                "id": str(notification.id),
                "id_usuario_destino": str(notification.id_usuario_destino),
                "id_usuario_origen": str(notification.id_usuario_origen),
                "id_publicacion": str(notification.id_publicacion) if notification.id_publicacion else "",
                "id_comentario": str(notification.id_comentario) if notification.id_comentario else "",
                "tipo": notification.tipo,
                "mensaje": notification.mensaje,
                "leida": notification.leida,
                "fecha_creacion": notification.fecha_creacion.isoformat(),
                "nombre_usuario_origen": f"{notification.usuario_origen.nombre} {notification.usuario_origen.apellido}".strip(),
                "username_usuario_origen": notification.usuario_origen.nombre_usuario
            })
        
        return converted_notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener notificaciones: {str(e)}"
        )

@router.put("/{notification_id}/read", summary="Marcar notificación como leída")
def mark_notification_as_read(
    notification_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marca una notificación específica como leída
    """
    try:
        notification = db.query(Notificacion).filter(
            Notificacion.id == notification_id,
            Notificacion.id_usuario_destino == str(current_user.id)
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
        
        notification.leida = True
        db.commit()
        
        return {"mensaje": "Notificación marcada como leída"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar notificación: {str(e)}"
        )

@router.put("/read-all", summary="Marcar todas las notificaciones como leídas")
def mark_all_notifications_as_read(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    try:
        notifications = db.query(Notificacion).filter(
            Notificacion.id_usuario_destino == str(current_user.id),
            Notificacion.leida == False
        ).all()
        
        for notification in notifications:
            notification.leida = True
        
        db.commit()
        
        return {"mensaje": f"{len(notifications)} notificaciones marcadas como leídas"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar notificaciones: {str(e)}"
        )

@router.get("/unread-count", summary="Obtener número de notificaciones no leídas")
def get_unread_notifications_count(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el número de notificaciones no leídas del usuario
    """
    try:
        count = db.query(Notificacion).filter(
            Notificacion.id_usuario_destino == str(current_user.id),
            Notificacion.leida == False
        ).count()
        
        return {"unread_count": count}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener conteo: {str(e)}"
        )
