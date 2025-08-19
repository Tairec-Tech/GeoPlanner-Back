from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.like import Like
from models.publicacion import Publicacion
from models.usuario import Usuario
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List
from uuid import UUID
import uuid

router = APIRouter()

# Esquemas para likes
class LikeResponse(BaseModel):
    id_usuario: str
    id_publicacion: str
    fecha_creacion: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }

class LikeCountResponse(BaseModel):
    id_publicacion: str
    total_likes: int
    usuarios_que_dieron_like: List[str]

@router.post("/{post_id}/like", response_model=dict, summary="Dar like a una publicación")
def like_post(
    post_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Da like a una publicación específica
    """
    try:
        # Validar que el ID de la publicación sea un UUID válido
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Verificar si el usuario ya dio like
        existing_like = db.query(Like).filter(
            Like.id_usuario == str(current_user.id),
            Like.id_publicacion == post_id
        ).first()
        
        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya has dado like a esta publicación"
            )
        
        # Crear nuevo like
        new_like = Like(
            id_usuario=str(current_user.id),
            id_publicacion=post_id
        )
        
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        
        return {
            "mensaje": "Like agregado exitosamente",
            "id_usuario": str(new_like.id_usuario),
            "id_publicacion": str(new_like.id_publicacion),
            "fecha_creacion": new_like.fecha_creacion.isoformat()
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al dar like: {str(e)}"
        )

@router.delete("/{post_id}/unlike", response_model=dict, summary="Quitar like de una publicación")
def unlike_post(
    post_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quita el like de una publicación específica
    """
    try:
        # Validar que el ID de la publicación sea un UUID válido
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Buscar el like existente
        existing_like = db.query(Like).filter(
            Like.id_usuario == str(current_user.id),
            Like.id_publicacion == post_id
        ).first()
        
        if not existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No has dado like a esta publicación"
            )
        
        # Eliminar el like
        db.delete(existing_like)
        db.commit()
        
        return {
            "mensaje": "Like removido exitosamente",
            "id_usuario": str(current_user.id),
            "id_publicacion": post_id
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al quitar like: {str(e)}"
        )

@router.get("/{post_id}/likes", response_model=LikeCountResponse, summary="Obtener información de likes de una publicación")
def get_post_likes(
    post_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene el total de likes y la lista de usuarios que dieron like a una publicación
    """
    try:
        # Validar que el ID de la publicación sea un UUID válido
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Obtener todos los likes de la publicación
        likes = db.query(Like).filter(Like.id_publicacion == post_id).all()
        
        # Extraer IDs de usuarios que dieron like
        usuarios_que_dieron_like = [str(like.id_usuario) for like in likes]
        
        return {
            "id_publicacion": post_id,
            "total_likes": len(likes),
            "usuarios_que_dieron_like": usuarios_que_dieron_like
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener likes: {str(e)}"
        )

@router.get("/user/{user_id}/likes", response_model=List[LikeResponse], summary="Obtener likes dados por un usuario")
def get_user_likes(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las publicaciones a las que un usuario ha dado like
    """
    try:
        # Validar que el ID de usuario sea un UUID válido
        uuid.UUID(user_id)
        
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener todos los likes del usuario
        likes = db.query(Like).filter(Like.id_usuario == user_id).all()
        
        # Convertir a formato de respuesta
        likes_response = []
        for like in likes:
            likes_response.append({
                "id_usuario": str(like.id_usuario),
                "id_publicacion": str(like.id_publicacion),
                "fecha_creacion": like.fecha_creacion.isoformat()
            })
        
        return likes_response
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener likes del usuario: {str(e)}"
        )
