from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Usuario
from typing import List
import uuid

router = APIRouter()

@router.get("/", summary="Obtener todos los usuarios")
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista de usuarios con paginación
    """
    try:
        users = db.query(Usuario).offset(skip).limit(limit).all()
        return users
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
