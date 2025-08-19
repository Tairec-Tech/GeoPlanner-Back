from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.actividadagenda import ActividadAgenda
from models.usuario import Usuario
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

class AgendaCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_actividad: datetime

class AgendaResponse(BaseModel):
    id: str
    id_usuario: str
    titulo: str
    descripcion: Optional[str]
    fecha_actividad: datetime
    fecha_creacion: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: str,
            datetime: lambda v: v.isoformat()
        }

@router.get("/", response_model=List[AgendaResponse], summary="Obtener actividades de la agenda del usuario autenticado")
def get_agenda(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        actividades = db.query(ActividadAgenda).filter(ActividadAgenda.id_usuario == str(current_user.id)).all()
        
        # Convertir UUIDs y datetimes a strings para la respuesta
        result = []
        for actividad in actividades:
            result.append({
                "id": str(actividad.id),
                "id_usuario": str(actividad.id_usuario),
                "titulo": actividad.titulo,
                "descripcion": actividad.descripcion,
                "fecha_actividad": actividad.fecha_actividad.isoformat(),
                "fecha_creacion": actividad.fecha_creacion.isoformat()
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener agenda: {str(e)}")

@router.post("/", response_model=AgendaResponse, summary="Crear actividad en la agenda")
def create_agenda_item(
    item: AgendaCreate, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        new_item = ActividadAgenda(
            id_usuario=str(current_user.id),
            titulo=item.titulo,
            descripcion=item.descripcion,
            fecha_actividad=item.fecha_actividad
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {
            "id": str(new_item.id),
            "id_usuario": str(new_item.id_usuario),
            "titulo": new_item.titulo,
            "descripcion": new_item.descripcion,
            "fecha_actividad": new_item.fecha_actividad.isoformat(),
            "fecha_creacion": new_item.fecha_creacion.isoformat()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear actividad: {str(e)}")

@router.get("/{actividad_id}", response_model=AgendaResponse, summary="Obtener actividad de agenda por ID")
def get_agenda_item(actividad_id: str, db: Session = Depends(get_db)):
    try:
        uuid.UUID(actividad_id)
        actividad = db.query(ActividadAgenda).filter(ActividadAgenda.id == actividad_id).first()
        if not actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return {
            "id": str(actividad.id),
            "id_usuario": str(actividad.id_usuario),
            "titulo": actividad.titulo,
            "descripcion": actividad.descripcion,
            "fecha_actividad": actividad.fecha_actividad.isoformat(),
            "fecha_creacion": actividad.fecha_creacion.isoformat()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de actividad inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener actividad: {str(e)}")

@router.put("/{actividad_id}", response_model=AgendaResponse, summary="Actualizar actividad de agenda")
def update_agenda_item(actividad_id: str, item: AgendaCreate, db: Session = Depends(get_db)):
    try:
        uuid.UUID(actividad_id)
        actividad = db.query(ActividadAgenda).filter(ActividadAgenda.id == actividad_id).first()
        if not actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        # Asignar a los atributos de instancia, no de clase
        setattr(actividad, "titulo", item.titulo)
        setattr(actividad, "descripcion", item.descripcion)
        setattr(actividad, "fecha_actividad", item.fecha_actividad)
        db.commit()
        db.refresh(actividad)
        return {
            "id": str(actividad.id),
            "id_usuario": str(actividad.id_usuario),
            "titulo": actividad.titulo,
            "descripcion": actividad.descripcion,
            "fecha_actividad": actividad.fecha_actividad.isoformat(),
            "fecha_creacion": actividad.fecha_creacion.isoformat()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de actividad inválido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar actividad: {str(e)}")

@router.delete("/{actividad_id}", summary="Eliminar actividad de agenda")
def delete_agenda_item(actividad_id: str, db: Session = Depends(get_db)):
    try:
        uuid.UUID(actividad_id)
        actividad = db.query(ActividadAgenda).filter(ActividadAgenda.id == actividad_id).first()
        if not actividad:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        db.delete(actividad)
        db.commit()
        return {"mensaje": "Actividad eliminada exitosamente"}
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de actividad inválido")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar actividad: {str(e)}")
