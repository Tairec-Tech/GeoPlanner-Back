from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from pydantic import BaseModel, EmailStr, validator
import bcrypt
import uuid
from uuid import UUID
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, OAuth2PasswordRequestForm
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
http_bearer = HTTPBearer(auto_error=False)

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
        
        # Convertir el user_id string a UUID
        user_uuid = uuid.UUID(user_id)
        user = db.query(Usuario).filter(Usuario.id == user_uuid).first()
        if user is None:
            raise credentials_exception
        return user
    except (JWTError, ValueError):
        raise credentials_exception

def get_current_user_optional(credentials: Optional[HTTPBearer] = Depends(http_bearer), db: Session = Depends(get_db)):
    """
    Versión opcional de get_current_user que no requiere autenticación
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # Convertir el user_id string a UUID
        user_uuid = uuid.UUID(user_id)
        user = db.query(Usuario).filter(Usuario.id == user_uuid).first()
        return user
    except (JWTError, ValueError):
        return None

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

# ========================================
# ENDPOINTS DE VERIFICACIÓN DE EMAIL
# ========================================

from fastapi import BackgroundTasks
from services.email_service import EmailService
import secrets

# Instanciar servicio de email
email_service = EmailService()

# Almacenamiento temporal de códigos (en producción usar Redis o base de datos)
verification_codes = {}

# Esquemas para verificación de email
class SendVerificationRequest(BaseModel):
    email: str
    username: str

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class ResendVerificationRequest(BaseModel):
    email: str

@router.post("/send-verification", summary="Enviar email de verificación")
async def send_verification_email(
    request: SendVerificationRequest,
    background_tasks: BackgroundTasks
):
    """Envía email de verificación"""
    try:
        # Generar código de verificación
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        
        # Guardar código con expiración (10 minutos)
        verification_codes[request.email] = {
            'code': verification_code,
            'username': request.username,
            'expires': datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Enviar email en background
        background_tasks.add_task(
            email_service.send_verification_email,
            request.email, request.username, verification_code
        )
        
        return {
            "message": "Email de verificación enviado exitosamente",
            "email": request.email,
            "expires_in": "10 minutos"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando email de verificación: {str(e)}"
        )

@router.post("/verify-email", summary="Verificar código de email")
async def verify_email(request: VerifyEmailRequest):
    """Verifica el código del email"""
    try:
        # Verificar si existe el código
        if request.email not in verification_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email no encontrado"
            )
        
        stored_data = verification_codes[request.email]
        
        # Verificar expiración
        if datetime.utcnow() > stored_data['expires']:
            del verification_codes[request.email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Código expirado"
            )
        
        # Verificar código
        if request.code != stored_data['code']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Código incorrecto"
            )
        
        # Código válido - limpiar y enviar email de bienvenida
        username = stored_data['username']
        del verification_codes[request.email]
        
        # Enviar email de bienvenida
        await email_service.send_welcome_email(request.email, username)
        
        return {
            "message": "Email verificado exitosamente",
            "username": username,
            "verified_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la verificación: {str(e)}"
        )

@router.post("/resend-verification", summary="Reenviar email de verificación")
async def resend_verification_email(
    request: ResendVerificationRequest,
    background_tasks: BackgroundTasks
):
    """Reenvía email de verificación"""
    try:
        if request.email not in verification_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Email no encontrado"
            )
        
        stored_data = verification_codes[request.email]
        username = stored_data['username']
        
        # Generar nuevo código
        new_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        
        # Actualizar código
        verification_codes[request.email] = {
            'code': new_code,
            'username': username,
            'expires': datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Enviar nuevo email
        background_tasks.add_task(
            email_service.send_verification_email,
            request.email, username, new_code
        )
        
        return {
            "message": "Nuevo código de verificación enviado",
            "email": request.email,
            "expires_in": "10 minutos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reenviando código: {str(e)}"
        )

