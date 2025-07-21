from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import EventoGuardado, Publicacion, Usuario
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

# Esquemas para eventos guardados
class SaveEventRequest(BaseModel):
    id_publicacion: str

class SavedEventResponse(BaseModel):
    id_usuario: str
    id_publicacion: str
    fecha_guardado: str
    
    class Config:
        from_attributes = True

@router.post("/", summary="Guardar evento")
def save_event(save_data: SaveEventRequest, user_id: str, db: Session = Depends(get_db)):
    """
    Guarda un evento (publicación) para un usuario
    """
    try:
        # Validar UUIDs
        uuid.UUID(user_id)
        uuid.UUID(save_data.id_publicacion)
        
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Verificar que la publicación existe
        publication = db.query(Publicacion).filter(Publicacion.id == save_data.id_publicacion).first()
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Verificar si ya está guardado
        existing_save = db.query(EventoGuardado).filter(
            EventoGuardado.id_usuario == user_id,
            EventoGuardado.id_publicacion == save_data.id_publicacion
        ).first()
        
        if existing_save:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El evento ya está guardado"
            )
        
        # Crear nuevo evento guardado
        new_saved_event = EventoGuardado(
            id_usuario=user_id,
            id_publicacion=save_data.id_publicacion
        )
        
        db.add(new_saved_event)
        db.commit()
        db.refresh(new_saved_event)
        
        return {"mensaje": "Evento guardado exitosamente", "evento_guardado": new_saved_event}
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar evento: {str(e)}"
        )

@router.delete("/{publication_id}", summary="Eliminar evento guardado")
def unsave_event(publication_id: str, user_id: str, db: Session = Depends(get_db)):
    """
    Elimina un evento guardado de la lista del usuario
    """
    try:
        # Validar UUIDs
        uuid.UUID(user_id)
        uuid.UUID(publication_id)
        
        # Buscar el evento guardado
        saved_event = db.query(EventoGuardado).filter(
            EventoGuardado.id_usuario == user_id,
            EventoGuardado.id_publicacion == publication_id
        ).first()
        
        if not saved_event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento guardado no encontrado"
            )
        
        db.delete(saved_event)
        db.commit()
        
        return {"mensaje": "Evento eliminado de guardados exitosamente"}
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID inválido"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar evento guardado: {str(e)}"
        )

@router.get("/", response_model=List[SavedEventResponse], summary="Obtener eventos guardados del usuario")
def get_saved_events(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los eventos guardados de un usuario
    """
    try:
        # Validar UUID
        uuid.UUID(user_id)
        
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener eventos guardados
        saved_events = db.query(EventoGuardado).filter(EventoGuardado.id_usuario == user_id).all()
        
        return saved_events
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos guardados: {str(e)}"
        )

@router.get("/with-details", summary="Obtener eventos guardados con detalles")
def get_saved_events_with_details(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los eventos guardados de un usuario con los detalles de la publicación
    """
    try:
        # Validar UUID
        uuid.UUID(user_id)
        
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener eventos guardados con JOIN a publicaciones
        saved_events_with_details = db.query(EventoGuardado, Publicacion).join(
            Publicacion, EventoGuardado.id_publicacion == Publicacion.id
        ).filter(EventoGuardado.id_usuario == user_id).all()
        
        # Formatear respuesta
        result = []
        for saved_event, publication in saved_events_with_details:
            result.append({
                "evento_guardado": {
                    "id_usuario": str(saved_event.id_usuario),
                    "id_publicacion": str(saved_event.id_publicacion),
                    "fecha_guardado": saved_event.fecha_guardado.isoformat()
                },
                "publicacion": {
                    "id": str(publication.id),
                    "texto": publication.texto,
                    "tipo": publication.tipo,
                    "fecha_evento": publication.fecha_evento.isoformat(),
                    "estado": publication.estado,
                    "id_autor": str(publication.id_autor)
                }
            })
        
        return result
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener eventos guardados: {str(e)}"
        )
