from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Amistad, Usuario
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

# Esquemas para amistades
class FriendshipRequest(BaseModel):
    id_usuario2: str

class FriendshipResponse(BaseModel):
    id_usuario1: str
    id_usuario2: str
    estado: str
    id_usuario_accion: str
    fecha_creacion: str
    
    class Config:
        from_attributes = True

@router.post("/request", summary="Enviar solicitud de amistad")
def send_friendship_request(friendship_data: FriendshipRequest, user_id: str, db: Session = Depends(get_db)):
    """
    Envía una solicitud de amistad a otro usuario
    """
    try:
        # Validar UUIDs
        uuid.UUID(user_id)
        uuid.UUID(friendship_data.id_usuario2)
        
        # Verificar que ambos usuarios existen
        user1 = db.query(Usuario).filter(Usuario.id == user_id).first()
        user2 = db.query(Usuario).filter(Usuario.id == friendship_data.id_usuario2).first()
        
        if not user1 or not user2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No se puede enviar solicitud a uno mismo
        if user_id == friendship_data.id_usuario2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes enviarte una solicitud de amistad a ti mismo"
            )
        
        # Ordenar los IDs para mantener consistencia (id1 < id2)
        id1, id2 = sorted([user_id, friendship_data.id_usuario2])
        
        # Verificar si ya existe una relación
        existing_friendship = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2
        ).first()
        
        if existing_friendship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una relación de amistad entre estos usuarios"
            )
        
        # Crear nueva solicitud de amistad
        new_friendship = Amistad(
            id_usuario1=id1,
            id_usuario2=id2,
            estado="pendiente",
            id_usuario_accion=user_id
        )
        
        db.add(new_friendship)
        db.commit()
        db.refresh(new_friendship)
        
        return {"mensaje": "Solicitud de amistad enviada", "amistad": new_friendship}
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar solicitud de amistad: {str(e)}"
        )

@router.put("/accept/{friend_id}", summary="Aceptar solicitud de amistad")
def accept_friendship(friend_id: str, user_id: str, db: Session = Depends(get_db)):
    """
    Acepta una solicitud de amistad pendiente
    """
    try:
        # Validar UUIDs
        uuid.UUID(user_id)
        uuid.UUID(friend_id)
        
        # Ordenar los IDs
        id1, id2 = sorted([user_id, friend_id])
        
        # Buscar la solicitud pendiente
        friendship = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2,
            Amistad.estado == "pendiente"
        ).first()
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de amistad no encontrada"
            )
        
        # Verificar que el usuario actual puede aceptar (no es quien envió la solicitud)
        if str(friendship.id_usuario_accion) == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes aceptar tu propia solicitud"
            )
        
        # Actualizar estado a aceptada
        friendship.estado = "aceptada"
        friendship.id_usuario_accion = user_id
        
        db.commit()
        db.refresh(friendship)
        
        return {"mensaje": "Solicitud de amistad aceptada", "amistad": friendship}
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al aceptar solicitud de amistad: {str(e)}"
        )

@router.get("/", response_model=List[FriendshipResponse], summary="Obtener amistades del usuario")
def get_user_friendships(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todas las amistades de un usuario
    """
    try:
        # Validar UUID
        uuid.UUID(user_id)
        
        # Buscar amistades donde el usuario aparece como usuario1 o usuario2
        friendships = db.query(Amistad).filter(
            (Amistad.id_usuario1 == user_id) | (Amistad.id_usuario2 == user_id)
        ).all()
        
        return friendships
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener amistades: {str(e)}"
        )

@router.get("/pending", response_model=List[FriendshipResponse], summary="Obtener solicitudes pendientes")
def get_pending_requests(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene las solicitudes de amistad pendientes para un usuario
    """
    try:
        # Validar UUID
        uuid.UUID(user_id)
        
        # Buscar solicitudes pendientes donde el usuario puede responder
        pending_requests = db.query(Amistad).filter(
            ((Amistad.id_usuario1 == user_id) | (Amistad.id_usuario2 == user_id)),
            Amistad.estado == "pendiente",
            Amistad.id_usuario_accion != user_id  # No incluir las que envió el usuario
        ).all()
        
        return pending_requests
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener solicitudes pendientes: {str(e)}"
        )
