from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Schemas para códigos QR
class QRCodeData(BaseModel):
    event_id: str
    user_id: str
    inscription_id: str
    timestamp: str
    signature: str

class QRCodeResponse(BaseModel):
    qr_code_data: str  # Datos JSON del QR
    qr_image_base64: str  # Imagen QR en base64
    inscription_id: str

# Schemas para verificación
class QRVerificationRequest(BaseModel):
    qr_data: str
    verificador_id: str
    ubicacion_lat: Optional[float] = None
    ubicacion_lng: Optional[float] = None
    notas: Optional[str] = None

class QRVerificationResponse(BaseModel):
    success: bool
    message: str
    user_name: Optional[str] = None
    event_title: Optional[str] = None
    verification_id: Optional[str] = None

# Schemas para historial de asistencia
class HistorialAsistenciaResponse(BaseModel):
    id: str
    id_inscripcion_usuario: str
    id_inscripcion_publicacion: str
    id_verificador: str
    estado_verificacion: str
    fecha_verificacion: datetime
    ubicacion_verificacion_lat: Optional[float] = None
    ubicacion_verificacion_lng: Optional[float] = None
    notas_verificacion: Optional[str] = None
    # Datos adicionales para mostrar
    nombre_usuario: str
    nombre_verificador: str
    titulo_evento: str

# Schemas para estadísticas
class EstadisticasAsistencia(BaseModel):
    total_inscritos: int
    total_asistieron: int
    total_no_asistieron: int
    porcentaje_asistencia: float
    estadisticas_genero: dict
    estadisticas_por_fecha: List[dict]
    estadisticas_por_hora: List[dict]

class EstadisticasGenero(BaseModel):
    masculino: int
    femenino: int
    otro: int
    total: int

class EstadisticasFecha(BaseModel):
    fecha: str
    inscritos: int
    asistieron: int
    porcentaje: float

class EstadisticasHora(BaseModel):
    hora: str
    cantidad: int
    porcentaje: float
