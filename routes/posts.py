from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.publicacion import Publicacion
from models.usuario import Usuario
from models.like import Like
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
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
    nombre_autor: str
    username_autor: str
    foto_autor: Optional[str] = None
    texto: str
    tipo: str
    fecha_evento: datetime
    privacidad: str
    media_url: Optional[str]
    terminos_adicionales: Optional[str]
    estado: str
    fecha_creacion: datetime
    likes: int = 0
    likers: List[str] = []
    rutas: Optional[List[dict]] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }

@router.get("/", response_model=List[PostResponse], summary="Obtener publicaciones del usuario autenticado")
def get_posts(
    skip: int = 0, 
    limit: int = 100, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las publicaciones del usuario autenticado y sus amigos
    """
    try:
        # Obtener publicaciones públicas y del usuario actual con información del autor
        posts = db.query(Publicacion).join(Usuario, Publicacion.id_autor == Usuario.id).filter(
            (Publicacion.privacidad == "publica") | 
            (Publicacion.id_autor == str(current_user.id))
        ).offset(skip).limit(limit).all()
        
        # Convertir UUIDs a strings para cada post y agregar información de likes
        converted_posts = []
        for post in posts:
            # Obtener información de likes
            likes = db.query(Like).filter(Like.id_publicacion == str(post.id)).all()
            likers = [str(like.id_usuario) for like in likes]
            
            # Obtener rutas de la publicación
            rutas = []
            if hasattr(post, 'rutas') and post.rutas:
                for ruta in post.rutas:
                    rutas.append({
                        "coords": ruta.coords,
                        "label": ruta.label
                    })
            
            converted_posts.append({
                "id": str(post.id),
                "id_autor": str(post.id_autor),
                "nombre_autor": f"{post.autor.nombre} {post.autor.apellido}".strip(),
                "username_autor": post.autor.nombre_usuario,
                "foto_autor": post.autor.foto_perfil_url,
                "texto": post.texto,
                "tipo": post.tipo,
                "fecha_evento": post.fecha_evento,
                "privacidad": post.privacidad,
                "media_url": post.media_url,
                "terminos_adicionales": post.terminos_adicionales,
                "estado": post.estado,
                "fecha_creacion": post.fecha_creacion,
                "likes": len(likes),
                "likers": likers,
                "rutas": rutas
            })
        
        return converted_posts
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
        
        post = db.query(Publicacion).join(Usuario, Publicacion.id_autor == Usuario.id).filter(Publicacion.id == post_id).first()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Obtener información de likes
        likes = db.query(Like).filter(Like.id_publicacion == post_id).all()
        likers = [str(like.id_usuario) for like in likes]
        
        # Obtener rutas de la publicación
        rutas = []
        if hasattr(post, 'rutas') and post.rutas:
            for ruta in post.rutas:
                rutas.append({
                    "coords": ruta.coords,
                    "label": ruta.label
                })
        
        # Convertir UUIDs a strings
        return {
            "id": str(post.id),
            "id_autor": str(post.id_autor),
            "nombre_autor": f"{post.autor.nombre} {post.autor.apellido}".strip(),
            "username_autor": post.autor.nombre_usuario,
            "foto_autor": post.autor.foto_perfil_url,
            "texto": post.texto,
            "tipo": post.tipo,
            "fecha_evento": post.fecha_evento,
            "privacidad": post.privacidad,
            "media_url": post.media_url,
            "terminos_adicionales": post.terminos_adicionales,
            "estado": post.estado,
            "fecha_creacion": post.fecha_creacion,
            "likes": len(likes),
            "likers": likers,
            "rutas": rutas
        }
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
def create_post(
    post_data: PostCreate, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva publicación para el usuario autenticado
    """
    try:
        # Crear nueva publicación
        new_post = Publicacion(
            id_autor=str(current_user.id),
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
        
        # Obtener información del autor
        autor = db.query(Usuario).filter(Usuario.id == current_user.id).first()
        
        # Convertir UUIDs a strings para la respuesta
        return {
            "id": str(new_post.id),
            "id_autor": str(new_post.id_autor),
            "nombre_autor": f"{autor.nombre} {autor.apellido}".strip(),
            "username_autor": autor.nombre_usuario,
            "foto_autor": autor.foto_perfil_url,
            "texto": new_post.texto,
            "tipo": new_post.tipo,
            "fecha_evento": new_post.fecha_evento,
            "privacidad": new_post.privacidad,
            "media_url": new_post.media_url,
            "terminos_adicionales": new_post.terminos_adicionales,
            "estado": new_post.estado,
            "fecha_creacion": new_post.fecha_creacion,
            "likes": 0,
            "likers": [],
            "rutas": []
        }
        
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
        
        posts = db.query(Publicacion).join(Usuario, Publicacion.id_autor == Usuario.id).filter(Publicacion.id_autor == user_id).all()
        
        # Convertir UUIDs a strings para cada post
        converted_posts = []
        for post in posts:
            # Obtener información de likes
            likes = db.query(Like).filter(Like.id_publicacion == str(post.id)).all()
            likers = [str(like.id_usuario) for like in likes]
            
            # Obtener rutas de la publicación
            rutas = []
            if hasattr(post, 'rutas') and post.rutas:
                for ruta in post.rutas:
                    rutas.append({
                        "coords": ruta.coords,
                        "label": ruta.label
                    })
            
            converted_posts.append({
                "id": str(post.id),
                "id_autor": str(post.id_autor),
                "nombre_autor": f"{post.autor.nombre} {post.autor.apellido}".strip(),
                "username_autor": post.autor.nombre_usuario,
                "foto_autor": post.autor.foto_perfil_url,
                "texto": post.texto,
                "tipo": post.tipo,
                "fecha_evento": post.fecha_evento,
                "privacidad": post.privacidad,
                "media_url": post.media_url,
                "terminos_adicionales": post.terminos_adicionales,
                "estado": post.estado,
                "fecha_creacion": post.fecha_creacion,
                "likes": len(likes),
                "likers": likers,
                "rutas": rutas
            })
        
        return converted_posts
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
