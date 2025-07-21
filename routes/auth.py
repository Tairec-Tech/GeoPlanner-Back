from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Usuario
from pydantic import BaseModel, EmailStr
import bcrypt
import uuid

router = APIRouter()

# Esquemas para autenticación
class UserRegister(BaseModel):
    nombre_usuario: str
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    fecha_nacimiento: str  # formato: YYYY-MM-DD

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    nombre_usuario: str
    email: str
    nombre: str
    apellido: str
    
    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse, summary="Registrar nuevo usuario")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema
    """
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(Usuario).filter(
            (Usuario.email == user_data.email) | 
            (Usuario.nombre_usuario == user_data.nombre_usuario)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email o nombre de usuario ya está registrado"
            )
        
        # Hashear la contraseña
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear nuevo usuario
        new_user = Usuario(
            nombre_usuario=user_data.nombre_usuario,
            email=user_data.email,
            password_hash=password_hash,
            nombre=user_data.nombre,
            apellido=user_data.apellido,
            fecha_nacimiento=user_data.fecha_nacimiento
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.post("/login", summary="Iniciar sesión")
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica un usuario y devuelve información básica
    """
    try:
        # Buscar usuario por email
        user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar contraseña
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        return {
            "mensaje": "Login exitoso",
            "usuario": {
                "id": str(user.id),
                "nombre_usuario": user.nombre_usuario,
                "email": user.email,
                "nombre": user.nombre,
                "apellido": user.apellido
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar sesión: {str(e)}"
        )
