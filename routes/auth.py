from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from pydantic import BaseModel, EmailStr, validator
import bcrypt
import uuid
from uuid import UUID
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import Optional

router = APIRouter()

# Esquemas para autenticación
class UserRegister(BaseModel):
    nombre_usuario: str
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    fecha_nacimiento: str  # formato: YYYY-MM-DD
    genero: Optional[str] = None
    biografia: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tema_preferido: Optional[str] = "default"
    foto_perfil_url: Optional[str] = None

class UserLogin(BaseModel):
    username_or_email: str  # Puede ser username o email
    password: str

class UserResponse(BaseModel):
    id: str
    nombre_usuario: str
    email: str
    nombre: str
    apellido: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }

# Configuración JWT
from config import config

SECRET_KEY = config['SECRET_KEY']
ALGORITHM = config['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

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
            fecha_nacimiento=user_data.fecha_nacimiento,
            genero=user_data.genero,
            biografia=user_data.biografia,
            latitud=user_data.latitud,
            longitud=user_data.longitud,
            ciudad=user_data.ciudad,
            pais=user_data.pais,
            tema_preferido=user_data.tema_preferido,
            foto_perfil_url=user_data.foto_perfil_url
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Convertir UUID a string para la respuesta
        return {
            "id": str(new_user.id),
            "nombre_usuario": new_user.nombre_usuario,
            "email": new_user.email,
            "nombre": new_user.nombre,
            "apellido": new_user.apellido
        }
        
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
        # Buscar usuario por email o nombre de usuario
        user = db.query(Usuario).filter(
            (Usuario.email == login_data.username_or_email) | 
            (Usuario.nombre_usuario == login_data.username_or_email)
        ).first()
        
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

@router.post("/token", summary="Obtener token JWT")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Buscar usuario por email o nombre de usuario
    user = db.query(Usuario).filter(
        (Usuario.email == form_data.username) | 
        (Usuario.nombre_usuario == form_data.username)
    ).first()
    
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoints secretos para administradores (no aparecen en docs)

