from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from models.publicacion import Publicacion
from models.like import Like
from routes.auth import get_current_user, get_current_user_optional
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
import uuid

router = APIRouter()

# Esquema para respuesta de usuarios
class UserListResponse(BaseModel):
    id: str
    nombre_usuario: str
    email: str
    nombre: str
    apellido: str
    verificado: bool
    fecha_creacion: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

# Esquema para actualización de perfil
class ProfileUpdateRequest(BaseModel):
    biografia: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tema_preferido: Optional[str] = None

@router.get("/me", summary="Obtener perfil del usuario actual")
def get_current_user_profile(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario autenticado
    """
    return {
        "id": str(current_user.id),
        "nombre_usuario": current_user.nombre_usuario,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "fecha_nacimiento": current_user.fecha_nacimiento,
        "genero": current_user.genero,
        "foto_perfil_url": current_user.foto_perfil_url,
        "biografia": current_user.biografia,
        "latitud": current_user.latitud,
        "longitud": current_user.longitud,
        "ciudad": current_user.ciudad,
        "pais": current_user.pais,
        "tema_preferido": current_user.tema_preferido,
        "verificado": current_user.verificado,
        "fecha_creacion": current_user.fecha_creacion
    }

@router.get("/all", response_model=List[UserListResponse], summary="Obtener todos los usuarios")
def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los usuarios del sistema
    """
    try:
        users = db.query(Usuario).offset(skip).limit(limit).all()
        
        # Convertir UUIDs a strings
        converted_users = []
        for user in users:
            converted_users.append({
                "id": str(user.id),
                "nombre_usuario": user.nombre_usuario,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido,
                "verificado": user.verificado,
                "fecha_creacion": user.fecha_creacion.isoformat()
            })
        
        return converted_users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}"
        )

@router.get("/blocked", summary="Obtener usuarios bloqueados por el usuario actual")
def get_blocked_users(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtiene la lista de usuarios bloqueados por el usuario actual
    """
    print(f"DEBUG: Endpoint /blocked llamado")
    print(f"DEBUG: Usuario actual ID: {current_user.id}")
    print(f"DEBUG: Usuario actual nombre: {current_user.nombre_usuario}")
    
    try:
        from models.amistad import Amistad
        
        # Buscar todas las relaciones de amistad donde el usuario actual está involucrado
        # y el estado es 'bloqueada'
        relaciones = db.query(Amistad).filter(
            ((Amistad.id_usuario1 == str(current_user.id)) | (Amistad.id_usuario2 == str(current_user.id))) &
            (Amistad.estado == 'bloqueada')
        ).all()
        
        print(f"DEBUG: Encontradas {len(relaciones)} relaciones de bloqueo")
        
        usuarios_bloqueados = []
        
        for relacion in relaciones:
            print(f"DEBUG: Procesando relación: {relacion.id_usuario1} - {relacion.id_usuario2}")
            print(f"DEBUG: Usuario actual ID (string): {str(current_user.id)}")
            print(f"DEBUG: Usuario actual ID (UUID): {current_user.id}")
            print(f"DEBUG: Relación usuario1 (tipo): {type(relacion.id_usuario1)}")
            print(f"DEBUG: Relación usuario2 (tipo): {type(relacion.id_usuario2)}")
            
            # Determinar cuál es el ID del usuario bloqueado
            # Convertir ambos a string para comparar
            if str(current_user.id) == str(relacion.id_usuario1):
                blocked_user_id = relacion.id_usuario2
                print(f"DEBUG: Usuario actual es usuario1, bloqueado es: {blocked_user_id}")
            elif str(current_user.id) == str(relacion.id_usuario2):
                blocked_user_id = relacion.id_usuario1
                print(f"DEBUG: Usuario actual es usuario2, bloqueado es: {blocked_user_id}")
            else:
                print(f"DEBUG: Usuario actual no encontrado en relación")
                continue  # Skip si el usuario actual no está en esta relación
            
            # Obtener información del usuario bloqueado
            blocked_user = db.query(Usuario).filter(Usuario.id == blocked_user_id).first()
            if blocked_user:
                usuarios_bloqueados.append({
                    "id": str(blocked_user.id),
                    "nombre_usuario": blocked_user.nombre_usuario,
                    "nombre": blocked_user.nombre,
                    "apellido": blocked_user.apellido,
                    "foto_perfil_url": blocked_user.foto_perfil_url,
                    "fecha_bloqueo": relacion.fecha_creacion.isoformat()
                })
                print(f"DEBUG: Agregado usuario bloqueado: {blocked_user.nombre_usuario}")
            else:
                print(f"DEBUG: Usuario bloqueado no encontrado: {blocked_user_id}")
        
        print(f"DEBUG: Total usuarios bloqueados: {len(usuarios_bloqueados)}")
        return usuarios_bloqueados
        
    except Exception as e:
        print(f"Error en get_blocked_users: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios bloqueados: {str(e)}"
        )

@router.get("/{user_id}", summary="Obtener usuario por ID")
def get_user(user_id: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtiene un usuario específico por su ID, excluyendo si hay bloqueo
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(user_id)
        
        # Verificar si hay bloqueo entre los usuarios
        from models.amistad import Amistad
        
        # Ordenar los IDs para buscar la relación
        id1, id2 = sorted([str(current_user.id), user_id])
        
        # Buscar relación de bloqueo
        block_relation = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2,
            Amistad.estado == "bloqueada"
        ).first()
        
        # Si hay bloqueo, no mostrar información del usuario
        if block_relation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes ver la información de este usuario"
            )
        
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Retornar información del usuario para perfil público
        return {
            "id": str(user.id),
            "nombre_usuario": user.nombre_usuario,
            "email": user.email,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "fecha_nacimiento": user.fecha_nacimiento,
            "genero": user.genero,
            "foto_perfil_url": user.foto_perfil_url,
            "biografia": user.biografia,
            "latitud": user.latitud,
            "longitud": user.longitud,
            "ciudad": user.ciudad,
            "pais": user.pais,
            "tema_preferido": user.tema_preferido,
            "verificado": user.verificado,
            "fecha_registro": user.fecha_creacion.isoformat()
        }
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
            detail=f"Error al obtener usuario: {str(e)}"
        )

@router.get("/{user_id}/posts", summary="Obtener publicaciones de un usuario")
def get_user_posts(user_id: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Obtiene todas las publicaciones de un usuario específico, excluyendo si hay bloqueo
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(user_id)
        
        # Verificar si hay bloqueo entre los usuarios
        from models.amistad import Amistad
        
        # Ordenar los IDs para buscar la relación
        id1, id2 = sorted([str(current_user.id), user_id])
        
        # Buscar relación de bloqueo
        block_relation = db.query(Amistad).filter(
            Amistad.id_usuario1 == id1,
            Amistad.id_usuario2 == id2,
            Amistad.estado == "bloqueada"
        ).first()
        
        # Si hay bloqueo, no mostrar publicaciones
        if block_relation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes ver las publicaciones de este usuario"
            )
        
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Obtener publicaciones del usuario
        posts = db.query(Publicacion).filter(Publicacion.id_autor == user_id).all()
        
        # Convertir a formato JSON
        converted_posts = []
        for post in posts:
            # Contar likes para esta publicación
            likes_count = db.query(Like).filter(Like.id_publicacion == post.id).count()
            
            # Obtener IDs de usuarios que dieron like
            likers = db.query(Like.id_usuario).filter(Like.id_publicacion == post.id).all()
            likers_ids = [str(like[0]) for like in likers]
            
            # Contar comentarios para esta publicación
            comments_count = len(post.comentarios) if post.comentarios else 0
            
            converted_posts.append({
                "id": str(post.id),
                "texto": post.texto,
                "fecha_creacion": post.fecha_creacion.isoformat(),
                "fecha_evento": post.fecha_evento.isoformat(),
                "privacidad": post.privacidad.value if post.privacidad else "publica",
                "media_url": post.media_url,
                "id_autor": str(post.id_autor),
                "nombre_autor": user.nombre + " " + user.apellido,
                "username_autor": user.nombre_usuario,
                "foto_autor": user.foto_perfil_url,
                "verificado": user.verificado,
                "likes": likes_count,
                "likers": likers_ids,
                "comentarios": [],  # Por ahora vacío, se puede implementar después
                "rutas": []  # Por ahora vacío, se puede implementar después
            })
        
        return converted_posts
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
            detail=f"Error al obtener publicaciones: {str(e)}"
        )

@router.put("/me", summary="Actualizar perfil del usuario actual")
def update_current_user_profile(
    profile_update: ProfileUpdateRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado
    """
    try:
        if profile_update.biografia is not None:
            current_user.biografia = profile_update.biografia
        if profile_update.latitud is not None:
            current_user.latitud = profile_update.latitud
        if profile_update.longitud is not None:
            current_user.longitud = profile_update.longitud
        if profile_update.ciudad is not None:
            current_user.ciudad = profile_update.ciudad
        if profile_update.pais is not None:
            current_user.pais = profile_update.pais
        if profile_update.tema_preferido is not None:
            current_user.tema_preferido = profile_update.tema_preferido
            
        db.commit()
        db.refresh(current_user)
        
        return {
            "mensaje": "Perfil actualizado correctamente",
            "usuario": {
                "id": str(current_user.id),
                "nombre_usuario": current_user.nombre_usuario,
                "email": current_user.email,
                "nombre": current_user.nombre,
                "apellido": current_user.apellido,
                "biografia": current_user.biografia,
                "latitud": current_user.latitud,
                "longitud": current_user.longitud,
                "ciudad": current_user.ciudad,
                "pais": current_user.pais,
                "tema_preferido": current_user.tema_preferido
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )

@router.get("/username/{username}", summary="Obtener usuario por nombre de usuario")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    Obtiene un usuario por su nombre de usuario
    """
    try:
        user = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )
