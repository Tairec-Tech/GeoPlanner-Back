from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Comentario, Publicacion, Usuario
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

# Esquemas para comentarios
class CommentCreate(BaseModel):
    texto: str

class CommentResponse(BaseModel):
    id: str
    id_publicacion: str
    id_autor: str
    texto: str
    fecha_creacion: str
    
    class Config:
        from_attributes = True

@router.get("/post/{post_id}", response_model=List[CommentResponse], summary="Obtener comentarios de una publicación")
def get_post_comments(post_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todos los comentarios de una publicación específica
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        comments = db.query(Comentario).filter(Comentario.id_publicacion == post_id).all()
        return comments
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener comentarios: {str(e)}"
        )

@router.post("/post/{post_id}", response_model=CommentResponse, summary="Crear comentario en una publicación")
def create_comment(post_id: str, comment_data: CommentCreate, author_id: str, db: Session = Depends(get_db)):
    """
    Crea un nuevo comentario en una publicación
    """
    try:
        # Validar UUIDs
        uuid.UUID(post_id)
        uuid.UUID(author_id)
        
        # Verificar que la publicación existe
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Verificar que el autor existe
        author = db.query(Usuario).filter(Usuario.id == author_id).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario autor no encontrado"
            )
        
        # Crear nuevo comentario
        new_comment = Comentario(
            id_publicacion=post_id,
            id_autor=author_id,
            texto=comment_data.texto
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        return new_comment
        
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
            detail=f"Error al crear comentario: {str(e)}"
        )

@router.get("/{comment_id}", response_model=CommentResponse, summary="Obtener comentario por ID")
def get_comment(comment_id: str, db: Session = Depends(get_db)):
    """
    Obtiene un comentario específico por su ID
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(comment_id)
        
        comment = db.query(Comentario).filter(Comentario.id == comment_id).first()
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario no encontrado"
            )
        return comment
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de comentario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener comentario: {str(e)}"
        )

@router.delete("/{comment_id}", summary="Eliminar comentario")
def delete_comment(comment_id: str, author_id: str, db: Session = Depends(get_db)):
    """
    Elimina un comentario (solo el autor puede eliminarlo)
    """
    try:
        # Validar UUIDs
        uuid.UUID(comment_id)
        uuid.UUID(author_id)
        
        comment = db.query(Comentario).filter(Comentario.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario no encontrado"
            )
        
        # Verificar que el usuario es el autor del comentario
        if str(comment.id_autor) != author_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este comentario"
            )
        
        db.delete(comment)
        db.commit()
        
        return {"mensaje": "Comentario eliminado exitosamente"}
        
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
            detail=f"Error al eliminar comentario: {str(e)}"
        )
