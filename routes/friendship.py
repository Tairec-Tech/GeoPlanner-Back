from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.amistad import Amistad
from models.usuario import Usuario
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

router = APIRouter()

# Esquemas para amistades
class FriendshipRequest(BaseModel):
    from_user_id: str
    to_user_id: str

class FriendshipResponse(BaseModel):
    id_usuario1: str
    id_usuario2: str
    estado: str
    id_usuario_accion: str
    fecha_creacion: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

# Esquema para estado de amistad
class FriendshipStatusResponse(BaseModel):
    status: str  # 'none', 'pending', 'accepted', 'blocked'
    isBlockedByMe: bool
    isBlockedByThem: bool

# Esquema para bloqueo
class BlockRequest(BaseModel):
    blocker_user_id: str
    blocked_user_id: str

@router.get("/status/{user_id1}/{user_id2}", summary="Obtener estado de amistad entre dos usuarios")
def get_friendship_status(user_id1: str, user_id2: str, db: Session = Depends(get_db)):
    """
    Obtiene el estado de amistad entre dos usuarios
    """
    try:
        # Validar UUIDs
        uuid.UUID(user_id1)
        uuid.UUID(user_id2)
        
        # Ordenar los IDs para mantener consistencia
        id1, id2 = sorted([user_id1, user_id2])
        
        # Buscar relación de amistad
        friendship = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2
        ).first()
        
        if not friendship:
            return {
                "status": "none",
                "isBlockedByMe": False,
                "isBlockedByThem": False
            }
        
        # Determinar el estado
        if friendship.estado == "pendiente":
            status = "pending"
        elif friendship.estado == "aceptada":
            status = "accepted"
        elif friendship.estado == "bloqueada":
            # Determinar quién bloqueó a quién
            if str(friendship.id_usuario_accion) == user_id1:
                isBlockedByMe = True
                isBlockedByThem = False
            else:
                isBlockedByMe = False
                isBlockedByThem = True
            return {
                "status": "blocked",
                "isBlockedByMe": isBlockedByMe,
                "isBlockedByThem": isBlockedByThem
            }
        else:
            status = "none"
        
        return {
            "status": status,
            "isBlockedByMe": False,
            "isBlockedByThem": False
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado de amistad: {str(e)}"
        )

@router.post("/request", summary="Enviar solicitud de amistad")
def send_friendship_request(friendship_data: FriendshipRequest, db: Session = Depends(get_db)):
    """
    Envía una solicitud de amistad a otro usuario
    """
    try:
        # Validar UUIDs
        uuid.UUID(friendship_data.from_user_id)
        uuid.UUID(friendship_data.to_user_id)
        
        # Verificar que ambos usuarios existen
        user1 = db.query(Usuario).filter(Usuario.id == friendship_data.from_user_id).first()
        user2 = db.query(Usuario).filter(Usuario.id == friendship_data.to_user_id).first()
        
        if not user1 or not user2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No se puede enviar solicitud a uno mismo
        if friendship_data.from_user_id == friendship_data.to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes enviarte una solicitud de amistad a ti mismo"
            )
        
        # Ordenar los IDs para mantener consistencia (id1 < id2)
        id1, id2 = sorted([friendship_data.from_user_id, friendship_data.to_user_id])
        
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
            id_usuario_accion=friendship_data.from_user_id
        )
        
        db.add(new_friendship)
        db.commit()
        db.refresh(new_friendship)
        
        return {
            "mensaje": "Solicitud de amistad enviada", 
            "amistad": {
                "id_usuario1": str(new_friendship.id_usuario1),
                "id_usuario2": str(new_friendship.id_usuario2),
                "estado": new_friendship.estado,
                "id_usuario_accion": str(new_friendship.id_usuario_accion),
                "fecha_creacion": new_friendship.fecha_creacion.isoformat()
            }
        }
        
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

@router.post("/block", summary="Bloquear usuario")
def block_user(block_data: BlockRequest, db: Session = Depends(get_db)):
    """
    Bloquea a un usuario
    """
    try:
        # Validar UUIDs
        uuid.UUID(block_data.blocker_user_id)
        uuid.UUID(block_data.blocked_user_id)
        
        # Verificar que ambos usuarios existen
        blocker = db.query(Usuario).filter(Usuario.id == block_data.blocker_user_id).first()
        blocked = db.query(Usuario).filter(Usuario.id == block_data.blocked_user_id).first()
        
        if not blocker or not blocked:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # No se puede bloquear a uno mismo
        if block_data.blocker_user_id == block_data.blocked_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes bloquearte a ti mismo"
            )
        
        # Ordenar los IDs para mantener consistencia
        id1, id2 = sorted([block_data.blocker_user_id, block_data.blocked_user_id])
        
        # Verificar si ya existe una relación
        existing_friendship = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2
        ).first()
        
        if existing_friendship:
            # Actualizar estado a bloqueada
            existing_friendship.estado = "bloqueada"
            existing_friendship.id_usuario_accion = block_data.blocker_user_id
        else:
            # Crear nueva relación bloqueada
            new_friendship = Amistad(
                id_usuario1=id1,
                id_usuario2=id2,
                estado="bloqueada",
                id_usuario_accion=block_data.blocker_user_id
            )
            db.add(new_friendship)
        
        db.commit()
        
        return {
            "mensaje": "Usuario bloqueado correctamente"
        }
        
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
            detail=f"Error al bloquear usuario: {str(e)}"
        )

@router.post("/unblock", summary="Desbloquear usuario")
def unblock_user(block_data: BlockRequest, db: Session = Depends(get_db)):
    """
    Desbloquea a un usuario
    """
    try:
        # Validar UUIDs
        uuid.UUID(block_data.blocker_user_id)
        uuid.UUID(block_data.blocked_user_id)
        
        # Ordenar los IDs para mantener consistencia
        id1, id2 = sorted([block_data.blocker_user_id, block_data.blocked_user_id])
        
        # Buscar la relación bloqueada
        friendship = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2,
            Amistad.estado == "bloqueada"
        ).first()
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe una relación de bloqueo entre estos usuarios"
            )
        
        # Verificar que el usuario actual es quien bloqueó
        if str(friendship.id_usuario_accion) != block_data.blocker_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo quien bloqueó puede desbloquear"
            )
        
        # Eliminar la relación de bloqueo
        db.delete(friendship)
        db.commit()
        
        return {
            "mensaje": "Usuario desbloqueado correctamente"
        }
        
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
            detail=f"Error al desbloquear usuario: {str(e)}"
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
        
        return {
            "mensaje": "Solicitud de amistad aceptada", 
            "amistad": {
                "id_usuario1": str(friendship.id_usuario1),
                "id_usuario2": str(friendship.id_usuario2),
                "estado": friendship.estado,
                "id_usuario_accion": str(friendship.id_usuario_accion),
                "fecha_creacion": friendship.fecha_creacion.isoformat()
            }
        }
        
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
        
        # Convertir UUIDs a strings
        converted_friendships = []
        for friendship in friendships:
            converted_friendships.append({
                "id_usuario1": str(friendship.id_usuario1),
                "id_usuario2": str(friendship.id_usuario2),
                "estado": friendship.estado,
                "id_usuario_accion": str(friendship.id_usuario_accion),
                "fecha_creacion": friendship.fecha_creacion.isoformat()
            })
        
        return converted_friendships
        
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
        
        # Convertir UUIDs a strings
        converted_requests = []
        for request in pending_requests:
            converted_requests.append({
                "id_usuario1": str(request.id_usuario1),
                "id_usuario2": str(request.id_usuario2),
                "estado": request.estado,
                "id_usuario_accion": str(request.id_usuario_accion),
                "fecha_creacion": request.fecha_creacion.isoformat()
            })
        
        return converted_requests
        
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

@router.delete("/request", summary="Cancelar solicitud de amistad")
def cancel_friendship_request(friendship_data: FriendshipRequest, db: Session = Depends(get_db)):
    """
    Cancela una solicitud de amistad pendiente
    """
    try:
        # Validar UUIDs
        uuid.UUID(friendship_data.from_user_id)
        uuid.UUID(friendship_data.to_user_id)
        
        # Ordenar los IDs para mantener consistencia
        id1, id2 = sorted([friendship_data.from_user_id, friendship_data.to_user_id])
        
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
        
        # Verificar que el usuario actual es quien envió la solicitud
        if str(friendship.id_usuario_accion) != friendship_data.from_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo quien envió la solicitud puede cancelarla"
            )
        
        # Eliminar la solicitud
        db.delete(friendship)
        db.commit()
        
        return {
            "mensaje": "Solicitud de amistad cancelada"
        }
        
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
            detail=f"Error al cancelar solicitud de amistad: {str(e)}"
        )

@router.delete("/friendship", summary="Dejar de ser amigos")
def remove_friendship(friendship_data: FriendshipRequest, db: Session = Depends(get_db)):
    """
    Elimina una relación de amistad existente
    """
    try:
        # Validar UUIDs
        uuid.UUID(friendship_data.from_user_id)
        uuid.UUID(friendship_data.to_user_id)
        
        # Ordenar los IDs para mantener consistencia
        id1, id2 = sorted([friendship_data.from_user_id, friendship_data.to_user_id])
        
        # Buscar la relación de amistad
        friendship = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2,
            Amistad.estado == "aceptada"
        ).first()
        
        if not friendship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relación de amistad no encontrada"
            )
        
        # Eliminar la amistad
        db.delete(friendship)
        db.commit()
        
        return {
            "mensaje": "Amistad eliminada correctamente"
        }
        
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
            detail=f"Error al eliminar amistad: {str(e)}"
        )

@router.get("/friends/{user_id}", summary="Obtener lista de amigos de un usuario")
def get_user_friends(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene la lista de amigos de un usuario específico
    """
    try:
        # Validar UUID
        uuid.UUID(user_id)
        
        # Buscar amistades aceptadas donde el usuario aparece
        friendships = db.query(Amistad).filter(
            ((Amistad.id_usuario1 == user_id) | (Amistad.id_usuario2 == user_id)),
            Amistad.estado == "aceptada"
        ).all()
        
        # Obtener información de los amigos
        friends = []
        for friendship in friendships:
            # Determinar cuál es el amigo (no el usuario actual)
            if str(friendship.id_usuario1) == user_id:
                friend_id = friendship.id_usuario2
            else:
                friend_id = friendship.id_usuario1
            
            # Obtener información del amigo
            friend = db.query(Usuario).filter(Usuario.id == friend_id).first()
            if friend:
                friends.append({
                    "id": str(friend.id),
                    "nombre": friend.nombre,
                    "apellido": friend.apellido,
                    "nombre_usuario": friend.nombre_usuario,
                    "foto_perfil_url": friend.foto_perfil_url,
                    "verificado": friend.verificado,
                    "fecha_amistad": friendship.fecha_creacion.isoformat()
                })
        
        return friends
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener amigos: {str(e)}"
        )
