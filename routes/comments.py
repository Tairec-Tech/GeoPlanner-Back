from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.comentario import Comentario
from models.publicacion import Publicacion
from models.usuario import Usuario
from models.notificacion import Notificacion
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import re

router = APIRouter()

# Esquemas para comentarios
class CommentCreate(BaseModel):
    texto: str
    id_comentario_padre: Optional[str] = None  # Para respuestas a comentarios

from uuid import UUID
from datetime import datetime

class CommentResponse(BaseModel):
    id: str
    id_publicacion: str
    id_autor: str
    nombre_autor: str
    username_autor: str
    foto_autor: Optional[str] = None
    texto: str
    fecha_creacion: str
    id_comentario_padre: Optional[str] = None
    respuestas: List['CommentResponse'] = []
    menciones: List[str] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

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
        
        # Obtener comentarios principales (sin padre) y sus respuestas
        comments = db.query(Comentario).join(Usuario, Comentario.id_autor == Usuario.id).filter(
            Comentario.id_publicacion == post_id,
            Comentario.id_comentario_padre.is_(None)
        ).all()
        
        # Convertir UUIDs y datetime a strings para cada comentario
        converted_comments = []
        for comment in comments:
            # Obtener respuestas del comentario
            respuestas = db.query(Comentario).join(Usuario, Comentario.id_autor == Usuario.id).filter(
                Comentario.id_comentario_padre == comment.id
            ).all()
            
            # Convertir respuestas
            respuestas_convertidas = []
            for respuesta in respuestas:
                menciones = json.loads(respuesta.menciones) if respuesta.menciones else []
                respuestas_convertidas.append({
                    "id": str(respuesta.id),
                    "id_publicacion": str(respuesta.id_publicacion),
                    "id_autor": str(respuesta.id_autor),
                    "nombre_autor": f"{respuesta.autor.nombre} {respuesta.autor.apellido}".strip(),
                    "username_autor": respuesta.autor.nombre_usuario,
                    "foto_autor": respuesta.autor.foto_perfil_url,
                    "texto": respuesta.texto,
                    "fecha_creacion": respuesta.fecha_creacion.isoformat(),
                    "id_comentario_padre": str(respuesta.id_comentario_padre),
                    "respuestas": [],
                    "menciones": menciones
                })
            
            # Obtener menciones del comentario principal
            menciones = json.loads(comment.menciones) if comment.menciones else []
            
            converted_comments.append({
                "id": str(comment.id),
                "id_publicacion": str(comment.id_publicacion),
                "id_autor": str(comment.id_autor),
                "nombre_autor": f"{comment.autor.nombre} {comment.autor.apellido}".strip(),
                "username_autor": comment.autor.nombre_usuario,
                "foto_autor": comment.autor.foto_perfil_url,
                "texto": comment.texto,
                "fecha_creacion": comment.fecha_creacion.isoformat(),
                "id_comentario_padre": None,
                "respuestas": respuestas_convertidas,
                "menciones": menciones
            })
        
        return converted_comments
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
def create_comment(
    post_id: str, 
    comment_data: CommentCreate, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo comentario en una publicación
    """
    try:
        # Validar UUID
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        post = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Validar comentario padre si se proporciona
        comentario_padre = None
        if comment_data.id_comentario_padre:
            try:
                uuid.UUID(comment_data.id_comentario_padre)
                comentario_padre = db.query(Comentario).filter(Comentario.id == comment_data.id_comentario_padre).first()
                if not comentario_padre:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Comentario padre no encontrado"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de comentario padre inválido"
                )
        
        # Crear nuevo comentario
        new_comment = Comentario(
            id_publicacion=post_id,
            id_autor=str(current_user.id),
            id_comentario_padre=comment_data.id_comentario_padre,
            texto=comment_data.texto
        )
        
        # Establecer menciones basadas en el texto
        new_comment.establecer_menciones()
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        # Obtener información del usuario para la respuesta
        user = db.query(Usuario).filter(Usuario.id == current_user.id).first()
        
        # Crear notificaciones para menciones
        menciones = new_comment.extraer_menciones()
        for username in menciones:
            usuario_mencionado = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
            if usuario_mencionado and str(usuario_mencionado.id) != str(current_user.id):
                notificacion = Notificacion(
                    id_usuario_destino=str(usuario_mencionado.id),
                    id_usuario_origen=str(current_user.id),
                    id_publicacion=post_id,
                    id_comentario=str(new_comment.id),
                    tipo="mencion",
                    mensaje=f"@{user.nombre_usuario} te mencionó en un comentario"
                )
                db.add(notificacion)
        
        # Crear notificación para respuesta si es una respuesta
        if comentario_padre and str(comentario_padre.id_autor) != str(current_user.id):
            notificacion_respuesta = Notificacion(
                id_usuario_destino=str(comentario_padre.id_autor),
                id_usuario_origen=str(current_user.id),
                id_publicacion=post_id,
                id_comentario=str(new_comment.id),
                tipo="respuesta",
                mensaje=f"@{user.nombre_usuario} respondió a tu comentario"
            )
            db.add(notificacion_respuesta)
        
        db.commit()
        
        # Convertir UUIDs y datetime a strings
        return {
            "id": str(new_comment.id),
            "id_publicacion": str(new_comment.id_publicacion),
            "id_autor": str(new_comment.id_autor),
            "nombre_autor": f"{user.nombre} {user.apellido}".strip(),
            "username_autor": user.nombre_usuario,
            "texto": new_comment.texto,
            "fecha_creacion": new_comment.fecha_creacion.isoformat(),
            "id_comentario_padre": comment_data.id_comentario_padre,
            "respuestas": [],
            "menciones": menciones
        }
        
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
        
        comment = db.query(Comentario).join(Usuario, Comentario.id_autor == Usuario.id).filter(Comentario.id == comment_id).first()
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comentario no encontrado"
            )
        
        # Convertir UUIDs y datetime a strings
        return {
            "id": str(comment.id),
            "id_publicacion": str(comment.id_publicacion),
            "id_autor": str(comment.id_autor),
            "nombre_autor": f"{comment.autor.nombre} {comment.autor.apellido}".strip(),
            "username_autor": comment.autor.nombre_usuario,
            "texto": comment.texto,
            "fecha_creacion": comment.fecha_creacion.isoformat()
        }
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
