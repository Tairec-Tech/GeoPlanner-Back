from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Publicacion, Usuario
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter()

# Esquemas para publicaciones
class PostCreate(BaseModel):
    texto: str
    tipo: str  # 'Deporte', 'Social', 'Estudio', 'Cultural', 'Otro'
    fecha_evento: datetime
    privacidad: str = "publica"  # 'publica', 'amigos', 'privada'
    media_url: Optional[str] = None
    terminos_adicionales: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    id_autor: str
    texto: str
    tipo: str
    fecha_evento: datetime
    privacidad: str
    media_url: Optional[str]
    terminos_adicionales: Optional[str]
    estado: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PostResponse], summary="Obtener todas las publicaciones")
def get_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista de publicaciones con paginación
    """
    try:
        posts = db.query(Publicacion).offset(skip).limit(limit).all()
        return posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener publicaciones: {str(e)}"
        )

@router.get("/{post_id}", response_model=PostResponse, summary="Obtener publicación por ID")
def get_post(post_id: str, db: Session = Depends(get_db)):
    """
    Obtiene una publicación específica por su ID
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(post_id)
        
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        return post
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener publicación: {str(e)}"
        )

@router.post("/", response_model=PostResponse, summary="Crear nueva publicación")
def create_post(post_data: PostCreate, author_id: str, db: Session = Depends(get_db)):
    """
    Crea una nueva publicación
    """
    try:
        # Validar que el autor existe
        uuid.UUID(author_id)
        author = db.query(Usuario).filter(Usuario.id == author_id).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario autor no encontrado"
            )
        
        # Crear nueva publicación
        new_post = Publicacion(
            id_autor=author_id,
            texto=post_data.texto,
            tipo=post_data.tipo,
            fecha_evento=post_data.fecha_evento,
            privacidad=post_data.privacidad,
            media_url=post_data.media_url,
            terminos_adicionales=post_data.terminos_adicionales
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return new_post
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de autor inválido"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear publicación: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[PostResponse], summary="Obtener publicaciones de un usuario")
def get_user_posts(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todas las publicaciones de un usuario específico
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(user_id)
        
        posts = db.query(Publicacion).filter(Publicacion.id_autor == user_id).all()
        return posts
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener publicaciones del usuario: {str(e)}"
        )
