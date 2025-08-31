from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional
import qrcode
import json
import base64
import io
import hashlib
from datetime import datetime, timedelta
import uuid

from database import get_db
from models.models import (
    Usuario, Publicacion, Inscripcion, HistorialAsistencia, 
    EstadoAsistenciaEnum, EstadoVerificacionQREnum
)
from schemas.qr_attendance import (
    QRCodeResponse, QRVerificationRequest, QRVerificationResponse,
    HistorialAsistenciaResponse, EstadisticasAsistencia
)
from routes.auth import get_current_user

router = APIRouter()

def generate_qr_signature(event_id: str, user_id: str, inscription_id: str, timestamp: str) -> str:
    """Genera una firma única para el código QR"""
    data = f"{event_id}:{user_id}:{inscription_id}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()

def create_qr_code_image(qr_data: str) -> str:
    """Crea una imagen QR y la convierte a base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir a base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

@router.post("/generate-qr/{event_id}/{user_id}", response_model=QRCodeResponse)
def generate_qr_code(
    event_id: str,
    user_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Genera un código QR para la inscripción de un usuario a un evento"""
    
    # Verificar que el usuario existe
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que el evento existe
    event = db.query(Publicacion).filter(Publicacion.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Verificar que el usuario está inscrito
    inscription = db.query(Inscripcion).filter(
        and_(
            Inscripcion.id_usuario == user_id,
            Inscripcion.id_publicacion == event_id
        )
    ).first()
    
    if not inscription:
        raise HTTPException(status_code=404, detail="Usuario no está inscrito en este evento")
    
    # Permitir QR para cualquier evento (público, amigos o privado)
    # Los QR son útiles para todos los tipos de eventos para verificar asistencia
    
    # Generar datos del QR
    timestamp = datetime.utcnow().isoformat()
    inscription_id = f"{user_id}_{event_id}"
    signature = generate_qr_signature(event_id, user_id, inscription_id, timestamp)
    
    qr_data = {
        "event_id": event_id,
        "user_id": user_id,
        "inscription_id": inscription_id,
        "timestamp": timestamp,
        "signature": signature
    }
    
    # Convertir a JSON string
    qr_json = json.dumps(qr_data)
    
    # Generar imagen QR
    qr_image_base64 = create_qr_code_image(qr_json)
    
    return QRCodeResponse(
        qr_code_data=qr_json,
        qr_image_base64=qr_image_base64,
        inscription_id=inscription_id
    )

@router.post("/verify-qr", response_model=QRVerificationResponse)
def verify_qr_code(
    verification_data: QRVerificationRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifica un código QR y registra la asistencia"""
    
    try:
        # Decodificar datos del QR
        qr_data = json.loads(verification_data.qr_data)
        
        # Verificar firma
        expected_signature = generate_qr_signature(
            qr_data["event_id"],
            qr_data["user_id"], 
            qr_data["inscription_id"],
            qr_data["timestamp"]
        )
        
        if qr_data["signature"] != expected_signature:
            raise HTTPException(status_code=400, detail="Código QR inválido")
        
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == qr_data["user_id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que el evento existe
        event = db.query(Publicacion).filter(Publicacion.id == qr_data["event_id"]).first()
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        
        # Verificar que el usuario está inscrito
        inscription = db.query(Inscripcion).filter(
            and_(
                Inscripcion.id_usuario == qr_data["user_id"],
                Inscripcion.id_publicacion == qr_data["event_id"]
            )
        ).first()
        
        if not inscription:
            raise HTTPException(status_code=404, detail="Usuario no está inscrito en este evento")
        
        # Verificar que no se haya verificado ya
        existing_verification = db.query(HistorialAsistencia).filter(
            and_(
                HistorialAsistencia.id_inscripcion_usuario == qr_data["user_id"],
                HistorialAsistencia.id_inscripcion_publicacion == qr_data["event_id"]
            )
        ).first()
        
        if existing_verification:
            return QRVerificationResponse(
                success=False,
                message="Este usuario ya fue verificado para este evento",
                user_name=f"{user.nombre} {user.apellido}",
                event_title=event.text[:50] + "..." if len(event.text) > 50 else event.text
            )
        
        # Crear registro de verificación
        verification = HistorialAsistencia(
            id_inscripcion_usuario=qr_data["user_id"],
            id_inscripcion_publicacion=qr_data["event_id"],
            id_verificador=verification_data.verificador_id,
            codigo_qr_data=verification_data.qr_data,
            estado_verificacion=EstadoVerificacionQREnum.verificado,
            ubicacion_verificacion_lat=verification_data.ubicacion_lat,
            ubicacion_verificacion_lng=verification_data.ubicacion_lng,
            notas_verificacion=verification_data.notas
        )
        
        db.add(verification)
        
        # Actualizar estado de asistencia
        inscription.estado_asistencia = EstadoAsistenciaEnum.asistio
        
        db.commit()
        
        return QRVerificationResponse(
            success=True,
            message="Asistencia verificada exitosamente",
            user_name=f"{user.nombre} {user.apellido}",
            event_title=event.text[:50] + "..." if len(event.text) > 50 else event.text,
            verification_id=str(verification.id)
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato de código QR inválido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al verificar código QR: {str(e)}")

@router.get("/historial/{event_id}", response_model=List[HistorialAsistenciaResponse])
def get_attendance_history(
    event_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de asistencia de un evento"""
    
    # Verificar que el evento existe
    event = db.query(Publicacion).filter(Publicacion.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Verificar que el usuario es el organizador del evento
    if event.id_autor != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el organizador puede ver el historial de asistencia")
    
    # Obtener historial
    historial = db.query(HistorialAsistencia).filter(
        HistorialAsistencia.id_inscripcion_publicacion == event_id
    ).all()
    
    result = []
    for record in historial:
        user = db.query(Usuario).filter(Usuario.id == record.id_inscripcion_usuario).first()
        verificador = db.query(Usuario).filter(Usuario.id == record.id_verificador).first()
        
        result.append(HistorialAsistenciaResponse(
            id=str(record.id),
            id_inscripcion_usuario=str(record.id_inscripcion_usuario),
            id_inscripcion_publicacion=str(record.id_inscripcion_publicacion),
            id_verificador=str(record.id_verificador),
            estado_verificacion=record.estado_verificacion.value,
            fecha_verificacion=record.fecha_verificacion,
            ubicacion_verificacion_lat=float(record.ubicacion_verificacion_lat) if record.ubicacion_verificacion_lat else None,
            ubicacion_verificacion_lng=float(record.ubicacion_verificacion_lng) if record.ubicacion_verificacion_lng else None,
            notas_verificacion=record.notas_verificacion,
            nombre_usuario=f"{user.nombre} {user.apellido}" if user else "Usuario desconocido",
            nombre_verificador=f"{verificador.nombre} {verificador.apellido}" if verificador else "Verificador desconocido",
            titulo_evento=event.text[:50] + "..." if len(event.text) > 50 else event.text
        ))
    
    return result

@router.get("/estadisticas/{event_id}", response_model=EstadisticasAsistencia)
def get_attendance_statistics(
    event_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene estadísticas detalladas de asistencia para un evento"""
    
    # Verificar que el evento existe
    event = db.query(Publicacion).filter(Publicacion.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Verificar que el usuario es el organizador del evento
    if event.id_autor != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el organizador puede ver las estadísticas")
    
    # Obtener totales
    total_inscritos = db.query(Inscripcion).filter(
        Inscripcion.id_publicacion == event_id
    ).count()
    
    total_asistieron = db.query(Inscripcion).filter(
        and_(
            Inscripcion.id_publicacion == event_id,
            Inscripcion.estado_asistencia == EstadoAsistenciaEnum.asistio
        )
    ).count()
    
    total_no_asistieron = db.query(Inscripcion).filter(
        and_(
            Inscripcion.id_publicacion == event_id,
            Inscripcion.estado_asistencia == EstadoAsistenciaEnum.no_asistio
        )
    ).count()
    
    porcentaje_asistencia = (total_asistieron / total_inscritos * 100) if total_inscritos > 0 else 0
    
    # Estadísticas por género
    stats_genero = db.query(
        Usuario.genero,
        func.count(Inscripcion.id_usuario).label('count')
    ).join(Inscripcion, Usuario.id == Inscripcion.id_usuario).filter(
        Inscripcion.id_publicacion == event_id
    ).group_by(Usuario.genero).all()
    
    estadisticas_genero = {
        'masculino': 0,
        'femenino': 0,
        'otro': 0
    }
    
    for stat in stats_genero:
        if stat.genero:
            estadisticas_genero[stat.genero.value.lower()] = stat.count
    
    # Estadísticas por fecha (últimos 7 días)
    fecha_inicio = datetime.utcnow() - timedelta(days=7)
    stats_fecha = db.query(
        func.date(HistorialAsistencia.fecha_verificacion).label('fecha'),
        func.count(HistorialAsistencia.id).label('count')
    ).filter(
        and_(
            HistorialAsistencia.id_inscripcion_publicacion == event_id,
            HistorialAsistencia.fecha_verificacion >= fecha_inicio
        )
    ).group_by(func.date(HistorialAsistencia.fecha_verificacion)).all()
    
    estadisticas_por_fecha = []
    for stat in stats_fecha:
        estadisticas_por_fecha.append({
            'fecha': stat.fecha.strftime('%Y-%m-%d'),
            'inscritos': total_inscritos,
            'asistieron': stat.count,
            'porcentaje': (stat.count / total_inscritos * 100) if total_inscritos > 0 else 0
        })
    
    # Estadísticas por hora
    stats_hora = db.query(
        extract('hour', HistorialAsistencia.fecha_verificacion).label('hora'),
        func.count(HistorialAsistencia.id).label('count')
    ).filter(
        HistorialAsistencia.id_inscripcion_publicacion == event_id
    ).group_by(extract('hour', HistorialAsistencia.fecha_verificacion)).all()
    
    estadisticas_por_hora = []
    for stat in stats_hora:
        estadisticas_por_hora.append({
            'hora': f"{int(stat.hora)}:00",
            'cantidad': stat.count,
            'porcentaje': (stat.count / total_asistieron * 100) if total_asistieron > 0 else 0
        })
    
    return EstadisticasAsistencia(
        total_inscritos=total_inscritos,
        total_asistieron=total_asistieron,
        total_no_asistieron=total_no_asistieron,
        porcentaje_asistencia=round(porcentaje_asistencia, 2),
        estadisticas_genero=estadisticas_genero,
        estadisticas_por_fecha=estadisticas_por_fecha,
        estadisticas_por_hora=estadisticas_por_hora
    )
