# 🚀 GeoPlanner Backend - API REST con FastAPI

## 📋 Descripción General

GeoPlanner Backend es la API REST robusta y escalable que alimenta la plataforma GeoPlanner, desarrollada con FastAPI y PostgreSQL. Esta API proporciona todos los servicios necesarios para la gestión de usuarios, eventos, autenticación, sistema QR y funcionalidades sociales de la plataforma.

### 🎯 Propósito del Backend
- **API REST completa** para todas las funcionalidades de GeoPlanner
- **Autenticación segura** con JWT y validación de datos
- **Base de datos relacional** con PostgreSQL y SQLAlchemy
- **Sistema de migraciones** con Alembic
- **Documentación automática** con Swagger/OpenAPI
- **Validación robusta** con Pydantic schemas

---

## 🏗️ Arquitectura Backend

### Stack Tecnológico
- **Framework**: FastAPI (Python 3.8+)
- **Base de Datos**: PostgreSQL 12+
- **ORM**: SQLAlchemy 2.0
- **Migraciones**: Alembic
- **Autenticación**: JWT (JSON Web Tokens)
- **Validación**: Pydantic schemas
- **Geocodificación**: OpenStreetMap Nominatim API
- **Testing**: pytest
- **Linting**: flake8

### Estructura de Carpetas
```
Geoplanner-Back/
├── models/            # Modelos de base de datos
│   └── models.py      # Definición de tablas y relaciones
├── routes/            # Endpoints de la API
│   ├── auth.py        # Autenticación y registro
│   ├── posts.py       # Gestión de publicaciones
│   ├── users.py       # Operaciones de usuarios
│   ├── friendship.py  # Sistema de amistades
│   ├── notifications.py # Sistema de notificaciones
│   ├── qr_attendance.py # Sistema QR y asistencia
│   └── agenda.py      # Agenda personal
├── schemas/           # Esquemas de validación Pydantic
│   ├── auth.py        # Esquemas de autenticación
│   ├── posts.py       # Esquemas de publicaciones
│   ├── users.py       # Esquemas de usuarios
│   └── qr_attendance.py # Esquemas QR y asistencia
├── auth/              # Utilidades de autenticación
│   └── auth.py        # Funciones JWT y verificación
├── database/          # Configuración de base de datos
│   └── database.py    # Conexión y configuración
├── config/            # Configuraciones del sistema
│   └── settings.py    # Variables de entorno
├── alembic/           # Migraciones de base de datos
│   ├── versions/      # Archivos de migración
│   └── env.py         # Configuración de Alembic
├── tests/             # Pruebas unitarias e integración
├── app.py            # Configuración principal de FastAPI
├── run.py            # Script de ejecución
└── requirements.txt  # Dependencias de Python
```

---

## 🚀 Características del Backend

### 🔐 Sistema de Autenticación
- **JWT Tokens**: Autenticación segura con expiración configurable
- **Registro en 3 pasos**: Validación progresiva de datos
- **Verificación de edad**: Cálculo preciso (mínimo 16 años)
- **Validación de contraseñas**: Fortaleza y patrones comunes
- **Protección de rutas**: Middleware de autenticación
- **Renovación automática**: Gestión de tokens expirados

### 👤 Gestión de Usuarios
- **CRUD completo**: Crear, leer, actualizar, eliminar usuarios
- **Perfiles personalizables**: Información personal y ubicación
- **Foto de perfil**: Almacenamiento y gestión de imágenes
- **Configuraciones de privacidad**: Control granular de datos
- **Búsqueda de usuarios**: Filtros por nombre, ubicación, intereses

### 📝 Sistema de Publicaciones
- **Tipos de eventos**: Social, Deporte, Estudio, Otros
- **Niveles de privacidad**: Público, Amigos, Privado
- **Ubicaciones múltiples**: Rutas con múltiples puntos
- **Fechas de evento**: Programación temporal
- **Filtros avanzados**: Por tipo, fecha, ubicación, privacidad
- **Relaciones complejas**: Autor, participantes, ubicaciones

### 👥 Sistema de Amistades
- **Estados de amistad**: Pendiente, Aceptada, Rechazada, Bloqueada
- **Solicitudes bidireccionales**: Envío y gestión
- **Notificaciones automáticas**: Alertas en tiempo real
- **Lista de amigos**: Gestión de relaciones
- **Usuarios bloqueados**: Prevención de interacciones

### 🔔 Sistema de Notificaciones
- **Tipos múltiples**: Amistad, actividad, asistencia
- **Estado de lectura**: Control de notificaciones leídas
- **Contador dinámico**: Número de no leídas
- **Notificaciones automáticas**: Eventos del sistema
- **Gestión completa**: Crear, leer, eliminar

### 📊 Sistema QR y Asistencia
- **Generación de QR**: Códigos únicos por inscripción
- **Verificación de asistencia**: Escaneo y registro
- **Historial completo**: Registro de todas las verificaciones
- **Estadísticas detalladas**: Métricas por evento
- **Ubicación de verificación**: Coordenadas de escaneo
- **Notas del verificador**: Información adicional

### 🗓️ Agenda Personal
- **Actividades personales**: Gestión de eventos propios
- **Recordatorios**: Notificaciones automáticas
- **Organización temporal**: Vista cronológica
- **Integración con eventos**: Sincronización automática

### 📍 Gestión de Ubicaciones
- **Geocodificación**: Conversión de direcciones a coordenadas
- **Validación de coordenadas**: Verificación de ubicaciones válidas
- **Rutas múltiples**: Múltiples puntos por evento
- **Ubicación por defecto**: Configuración inicial
- **Búsqueda geográfica**: Eventos por proximidad

---

## 🔧 Configuración e Instalación

### Requisitos Previos
- **Python** 3.8+
- **PostgreSQL** 12+
- **pip** (gestor de paquetes Python)
- **Git** (control de versiones)

### Instalación Rápida
```bash
# Clonar el repositorio
git clone <repository-url>
cd Geoplanner-Back

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones de base de datos y JWT

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Scripts Disponibles
```bash
uvicorn app:app --reload   # Servidor de desarrollo
alembic upgrade head       # Aplicar migraciones
alembic revision --autogenerate  # Generar nueva migración
pytest                     # Ejecutar pruebas
flake8                     # Verificar código
```

### Comandos de Ejecución Alternativos

**Desarrollo local (solo localhost):**
```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Desarrollo con acceso externo:**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Producción (sin reload):**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

**Con configuración personalizada:**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000 --log-level info
```

### Solución de Problemas Comunes

**Error: "No module named 'uvicorn'"**
- **Causa**: Uvicorn no está instalado
- **Solución**: 
  ```bash
  pip install uvicorn
  # O instalar todas las dependencias
  pip install -r requirements.txt
  ```

**Error: "Connection refused" en base de datos**
- **Causa**: PostgreSQL no está ejecutándose o las credenciales son incorrectas
- **Solución**: 
  ```bash
  # Verificar que PostgreSQL esté ejecutándose
  sudo systemctl status postgresql
  
  # Crear base de datos si no existe
  createdb geoplanner
  
  # Verificar conexión
  psql -h localhost -U usuario -d geoplanner
  ```

**Error: "SECRET_KEY not set"**
- **Causa**: Variable de entorno SECRET_KEY no configurada
- **Solución**: Configurar en archivo `.env`:
  ```env
  SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui_cambiala_por_una_real
  ```

**Error: "Port already in use"**
- **Causa**: Puerto 8000 ya está ocupado
- **Solución**: Cambiar puerto en `.env`:
  ```env
  PORT=8001
  ```

**Error: "Module not found"**
- **Causa**: Dependencias no instaladas
- **Solución**: 
  ```bash
  pip install -r requirements.txt
  ```

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto basado en `env.example`:

**Variables Obligatorias:**
```env
# Base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/geoplanner

# Autenticación JWT (¡CAMBIA LA CLAVE SECRETA!)
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui_cambiala_por_una_real
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS (orígenes permitidos)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Geocodificación
NOMINATIM_URL=https://nominatim.openstreetmap.org
```

**Variables Opcionales:**
```env
# Cloudinary (para subida de imágenes)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# SMTP (para envío de emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
```

---

## 🗄️ Modelos de Base de Datos

### Usuario (`usuarios`)
```python
class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    contraseña_hash = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(Enum(TipoGeneroEnum), nullable=False)
    latitud = Column(Numeric(9, 6), nullable=False)
    longitud = Column(Numeric(9, 6), nullable=False)
    foto_perfil = Column(String(255))
    fecha_registro = Column(TIMESTAMP(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True)
```

### Publicación (`publicaciones`)
```python
class Publicacion(Base):
    __tablename__ = 'publicaciones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_autor = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    texto = Column(Text, nullable=False)
    tipo = Column(Enum(TipoPublicacionEnum), nullable=False)
    privacidad = Column(Enum(TipoPrivacidadEnum), nullable=False)
    fecha_evento = Column(TIMESTAMP(timezone=True))
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado = Column(Enum(EstadoPublicacionEnum), default=EstadoPublicacionEnum.activa)
```

### Ruta (`rutas`)
```python
class Ruta(Base):
    __tablename__ = 'rutas'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id'), nullable=False)
    latitud = Column(Numeric(9, 6), nullable=False)
    longitud = Column(Numeric(9, 6), nullable=False)
    orden = Column(Integer, nullable=False)
    descripcion = Column(String(255))
```

### Inscripción (`inscripciones`)
```python
class Inscripcion(Base):
    __tablename__ = 'inscripciones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    id_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id'), nullable=False)
    fecha_inscripcion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    estado_asistencia = Column(Enum(EstadoAsistenciaEnum), default=EstadoAsistenciaEnum.pendiente)
```

### Amistad (`amistades`)
```python
class Amistad(Base):
    __tablename__ = 'amistades'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario_origen = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    id_usuario_destino = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    estado = Column(Enum(EstadoAmistadEnum), default=EstadoAmistadEnum.pendiente)
    fecha_solicitud = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_respuesta = Column(TIMESTAMP(timezone=True))
```

### Notificación (`notificaciones`)
```python
class Notificacion(Base):
    __tablename__ = 'notificaciones'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario_destino = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    tipo = Column(Enum(TipoNotificacionEnum), nullable=False)
    titulo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
```

### Historial de Asistencia (`historialasistencia`)
```python
class HistorialAsistencia(Base):
    __tablename__ = 'historialasistencia'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_inscripcion_usuario = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    id_inscripcion_publicacion = Column(UUID(as_uuid=True), ForeignKey('publicaciones.id'), nullable=False)
    id_verificador = Column(UUID(as_uuid=True), ForeignKey('usuarios.id'), nullable=False)
    codigo_qr_data = Column(Text, nullable=False)
    estado_verificacion = Column(Enum(EstadoVerificacionQREnum), nullable=False)
    fecha_verificacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ubicacion_verificacion_lat = Column(Numeric(9, 6))
    ubicacion_verificacion_lng = Column(Numeric(9, 6))
    notas_verificacion = Column(Text)
```

---

## 🌐 Endpoints de la API

### Autenticación (`/auth`)
```python
POST /auth/token              # Login de usuario
POST /auth/register           # Registro de usuario
GET  /auth/me                 # Obtener usuario actual
POST /auth/refresh            # Renovar token
POST /auth/logout             # Cerrar sesión
```

### Usuarios (`/users`)
```python
GET    /users/                # Listar usuarios (con filtros)
GET    /users/{user_id}       # Obtener usuario específico
PUT    /users/{user_id}       # Actualizar usuario
DELETE /users/{user_id}       # Eliminar usuario
GET    /users/{user_id}/posts # Posts de un usuario
```

### Publicaciones (`/posts`)
```python
GET    /posts/                # Listar publicaciones
POST   /posts/                # Crear publicación
GET    /posts/{post_id}       # Obtener publicación
PUT    /posts/{post_id}       # Actualizar publicación
DELETE /posts/{post_id}       # Eliminar publicación
POST   /posts/{post_id}/inscribirse    # Inscribirse en evento
DELETE /posts/{post_id}/desinscribirse # Desinscribirse de evento
```

### Amistades (`/friendship`)
```python
POST /friendship/request      # Enviar solicitud de amistad
PUT  /friendship/accept/{friend_id}    # Aceptar solicitud
PUT  /friendship/reject/{friend_id}    # Rechazar solicitud
PUT  /friendship/block/{friend_id}     # Bloquear usuario
PUT  /friendship/unblock/{friend_id}   # Desbloquear usuario
GET  /friendship/friends      # Listar amigos
GET  /friendship/pending      # Solicitudes pendientes
```

### Notificaciones (`/notifications`)
```python
GET    /notifications/        # Listar notificaciones
GET    /notifications/unread-count     # Contador de no leídas
PUT    /notifications/{notification_id}/read  # Marcar como leída
DELETE /notifications/{notification_id}       # Eliminar notificación
```

### QR y Asistencia (`/qr-attendance`)
```python
POST /qr-attendance/generate-qr/{event_id}/{user_id}  # Generar QR
POST /qr-attendance/verify-qr                         # Verificar QR
GET  /qr-attendance/historial/{event_id}              # Historial de asistencia
GET  /qr-attendance/estadisticas/{event_id}           # Estadísticas del evento
```

### Agenda (`/agenda`)
```python
GET    /agenda/               # Listar actividades del usuario
POST   /agenda/               # Crear actividad
GET    /agenda/{activity_id}  # Obtener actividad
PUT    /agenda/{activity_id}  # Actualizar actividad
DELETE /agenda/{activity_id}  # Eliminar actividad
```

---

## 🔐 Sistema de Autenticación

### JWT Implementation
```python
# Generación de token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verificación de token
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
```

### Middleware de Autenticación
```python
# Dependency para obtener usuario actual
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = get_user_by_email(db, email=username)
    if user is None:
        raise credentials_exception
    return user
```

---

## 📊 Validación de Datos

### Pydantic Schemas
```python
# Ejemplo de schema para usuario
class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    contraseña: str = Field(..., min_length=8)
    fecha_nacimiento: date
    genero: TipoGeneroEnum
    latitud: Decimal = Field(..., ge=-90, le=90)
    longitud: Decimal = Field(..., ge=-180, le=180)

# Ejemplo de schema para publicación
class PostCreate(BaseModel):
    texto: str = Field(..., min_length=1, max_length=1000)
    tipo: TipoPublicacionEnum
    privacidad: TipoPrivacidadEnum
    fecha_evento: Optional[datetime] = None
    rutas: List[RouteCreate] = Field(default_factory=list)
```

### Validaciones Personalizadas
```python
# Validación de edad mínima
def validate_minimum_age(fecha_nacimiento: date) -> bool:
    today = date.today()
    age = today.year - fecha_nacimiento.year
    if today.month < fecha_nacimiento.month or (today.month == fecha_nacimiento.month and today.day < fecha_nacimiento.day):
        age -= 1
    return age >= 16

# Validación de contraseña
def validate_password_strength(password: str) -> dict:
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    return {"score": score, "feedback": feedback}
```

---

## 🗺️ Sistema de Geocodificación

### Integración con Nominatim
```python
async def geocode_address(address: str) -> Optional[dict]:
    """Convierte una dirección en coordenadas usando OpenStreetMap Nominatim"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NOMINATIM_URL}/search",
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1
                }
            )
            data = response.json()
            
            if data:
                location = data[0]
                return {
                    "lat": float(location["lat"]),
                    "lng": float(location["lon"]),
                    "display_name": location["display_name"]
                }
    except Exception as e:
        logger.error(f"Error en geocodificación: {e}")
        return None
```

### Validación de Coordenadas
```python
def validate_coordinates(lat: float, lng: float) -> bool:
    """Valida que las coordenadas estén en rangos válidos"""
    return -90 <= lat <= 90 and -180 <= lng <= 180

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calcula la distancia entre dos puntos usando la fórmula de Haversine"""
    R = 6371  # Radio de la Tierra en kilómetros
    
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c
```

---

## 📊 Sistema QR y Asistencia

### Generación de Códigos QR
```python
def generate_qr_signature(event_id: str, user_id: str, timestamp: str) -> str:
    """Genera una firma única para el código QR"""
    data = f"{event_id}:{user_id}:{timestamp}"
    return hashlib.sha256(data.encode()).hexdigest()

def create_qr_code_image(qr_data: str) -> str:
    """Crea una imagen QR y la convierte a base64"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
```

### Verificación de Asistencia
```python
async def verify_qr_code(qr_data: str, verifier_id: str, location: dict) -> dict:
    """Verifica un código QR y registra la asistencia"""
    try:
        # Decodificar datos del QR
        event_id, user_id, timestamp = qr_data.split(":")
        
        # Verificar que la inscripción existe
        inscription = get_inscription(db, user_id, event_id)
        if not inscription:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")
        
        # Crear registro de verificación
        verification = HistorialAsistencia(
            id_inscripcion_usuario=user_id,
            id_inscripcion_publicacion=event_id,
            id_verificador=verifier_id,
            codigo_qr_data=qr_data,
            estado_verificacion=EstadoVerificacionQREnum.verificado,
            ubicacion_verificacion_lat=location.get("lat"),
            ubicacion_verificacion_lng=location.get("lng")
        )
        
        db.add(verification)
        db.commit()
        
        return {"success": True, "message": "Asistencia verificada"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 🔒 Seguridad y Validación

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/token")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # Implementación del login
    pass
```

### Validación de Entrada
```python
from pydantic import validator

class PostCreate(BaseModel):
    texto: str = Field(..., min_length=1, max_length=1000)
    
    @validator('texto')
    def validate_texto(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('El texto no puede estar vacío')
        return v.strip()
```

---

## 🧪 Testing

### Configuración de Pruebas
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///./test.db")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    return TestClient(app)
```

### Ejemplos de Pruebas
```python
# test_auth.py
def test_register_user(client):
    response = client.post("/auth/register", json={
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan@example.com",
        "contraseña": "password123",
        "fecha_nacimiento": "1990-01-01",
        "genero": "masculino",
        "latitud": 10.654,
        "longitud": -71.612
    })
    assert response.status_code == 201
    assert response.json()["email"] == "juan@example.com"

def test_login_user(client):
    response = client.post("/auth/token", data={
        "username": "juan@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 📦 Despliegue

### Configuración de Producción
```python
# settings.py
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/geoplanner
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=geoplanner
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 📊 Monitoreo y Logging

### Configuración de Logs
```python
import logging
from logging.handlers import RotatingFileHandler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('geoplanner.log', maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Métricas de Rendimiento
```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 🔧 Herramientas de Desarrollo

### Makefile
```makefile
# Makefile
.PHONY: install run test lint migrate

install:
	pip install -r requirements.txt

run:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

dev:
	uvicorn app:app --reload --host 127.0.0.1 --port 8000

test:
	pytest -v

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(message)"
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

---

## 🤝 Contribución

### Estándares de Código
- **PEP 8**: Estilo de código Python
- **Type hints**: Anotaciones de tipo obligatorias
- **Docstrings**: Documentación de funciones y clases
- **Tests**: Cobertura mínima del 80%

### Flujo de Desarrollo
1. **Fork** del repositorio
2. **Branch** para nueva funcionalidad
3. **Desarrollo** con tests
4. **Pull Request** con descripción
5. **Code Review** y aprobación
6. **Merge** a main

---

## 📞 Soporte

### Documentación
- **API Docs**: http://localhost:8000/docs (Swagger)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Contacto
- **Equipo**: Desarrolladores GeoPlanner
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

*GeoPlanner Backend - API robusta para conectar personas* 🚀✨ 