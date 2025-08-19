from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from routes.auth import get_current_user
from typing import List
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

@router.get("/{user_id}", summary="Obtener usuario por ID")
def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene un usuario específico por su ID
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(user_id)
        
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )
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

@router.put("/me", summary="Actualizar perfil del usuario actual")
def update_current_user_profile(
    biografia: str = None,
    latitud: float = None,
    longitud: float = None,
    ciudad: str = None,
    pais: str = None,
    tema_preferido: str = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el perfil del usuario autenticado
    """
    try:
        if biografia is not None:
            current_user.biografia = biografia
        if latitud is not None:
            current_user.latitud = latitud
        if longitud is not None:
            current_user.longitud = longitud
        if ciudad is not None:
            current_user.ciudad = ciudad
        if pais is not None:
            current_user.pais = pais
        if tema_preferido is not None:
            current_user.tema_preferido = tema_preferido
            
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
