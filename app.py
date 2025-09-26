from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Importar Base y engine para crear tablas
from database import Base, engine

# Importar todas las rutas (eliminamos agenda)
from routes.users import router as user_router
from routes.auth import router as auth_router
from routes.posts import router as post_router
from routes.comments import router as comment_router
from routes.friendship import router as friendship_router
from routes.saved_event import router as saved_event_router
from routes.agenda import router as agenda_router
from routes.likes import router as like_router
from routes.notifications import router as notification_router
from routes.upload import router as upload_router
from routes.qr_attendance import router as qr_attendance_router
from routes.configuracion_usuario import router as configuracion_router

# Crear tablas automáticamente
Base.metadata.create_all(engine)

# Instancia principal de la aplicación
app = FastAPI(
    title="GeoPlanner API",
    description="REST API para la red social GeoPlanner",
    version="5.0.0",
    # Configuración de seguridad para Swagger
    openapi_tags=[
        {
            "name": "Autenticación",
            "description": "Endpoints para login, registro y gestión de tokens JWT"
        },
        {
            "name": "Usuarios", 
            "description": "Gestión de perfiles de usuario y configuraciones"
        },
        {
            "name": "Publicaciones",
            "description": "Creación y gestión de rutas y publicaciones"
        },
        {
            "name": "Comentarios",
            "description": "Sistema de comentarios en rutas"
        },
        {
            "name": "Amistades",
            "description": "Sistema de amigos y conexiones sociales"
        },
        {
            "name": "Eventos Guardados",
            "description": "Guardado y gestión de eventos favoritos"
        },
        {
            "name": "Agenda",
            "description": "Gestión de agenda personal y eventos"
        },
        {
            "name": "Likes",
            "description": "Sistema de likes y reacciones"
        },
        {
            "name": "Notificaciones",
            "description": "Sistema de notificaciones en tiempo real"
        },
        {
            "name": "Subida de Archivos",
            "description": "Gestión de archivos e imágenes"
        },
        {
            "name": "QR y Asistencia",
            "description": "Sistema de códigos QR para asistencia a eventos"
        },
        {
            "name": "Configuraciones de Usuario",
            "description": "Preferencias y configuraciones personalizadas"
        }
    ]
)

# Configurar esquema de seguridad para Swagger
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi

# Esquema de seguridad Bearer
security_scheme = HTTPBearer(
    scheme_name="Bearer",
    bearerFormat="JWT",
    description="Ingresa tu token JWT obtenido del endpoint /auth/login"
)

# Función personalizada para OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="GeoPlanner API",
        version="5.0.0",
        description="""
        ## GeoPlanner API - Red Social de Rutas y Eventos

        ### 🔐 Autenticación
        Para acceder a endpoints protegidos:
        1. Haz POST a `/auth/login` con `username_or_email` y `password`
        2. Copia el `access_token` de la respuesta
        3. Haz clic en "Authorize" (🔒) arriba y pega el token
        4. Ahora puedes usar todos los endpoints protegidos

        ### 📍 Funcionalidades Principales
        - **Rutas**: Crear y compartir rutas geolocalizadas
        - **Eventos**: Organizar y asistir a eventos
        - **Social**: Sistema de amigos, likes y comentarios
        - **QR**: Códigos QR para asistencia a eventos
        - **Temas**: Personalización de interfaz

        ### 🚀 Endpoints Principales
        - `POST /auth/login` - Iniciar sesión
        - `POST /auth/register` - Registro de usuario
        - `GET /posts` - Obtener rutas públicas
        - `POST /posts` - Crear nueva ruta
        - `GET /users/me` - Perfil del usuario actual
        """,
        routes=app.routes,
    )
    
    # Agregar esquema de seguridad
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtenido del endpoint de login"
        }
    }
    
    # No aplicar seguridad automáticamente - dejar que cada endpoint maneje su propia seguridad
    # Los endpoints que necesitan autenticación ya tienen Depends(get_current_user)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="public"), name="static")

# Lista de orígenes permitidos (de dónde puede venir la solicitud)
# Para desarrollo, puedes permitir el origen de tu app de React.
# Si usas Vite, suele ser 'http://localhost:5173' o 'http://localhost:5174'.
origins = [
    "http://localhost:5173",
    "http://localhost:5174",  # Puerto alternativo de Vite
    "http://localhost:3000",  # Si usas Create React App
    "https://geoplanner-front.vercel.app",  # Tu frontend en Vercel
    "https://geoplanner.vercel.app",  # Alternativa
    "https://geoplanner-0uva.onrender.com",  # Tu frontend en Render
    "https://*.onrender.com",  # Permitir cualquier subdominio de Render
    # Añade aquí la URL de tu frontend si está en producción
]

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Manejo global de excepciones de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detalle": exc.errors(), "mensaje": "Error de validación"}
    )

# Endpoint raíz para verificar que el servidor funciona
@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a GeoPlanner API", "version": "5.0.0", "estado": "activo"}

# Endpoints de prueba eliminados

# Registrar todos los routers (incluyendo agenda)
app.include_router(user_router, prefix="/users", tags=["Usuarios"])
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(post_router, prefix="/posts", tags=["Publicaciones"])
app.include_router(comment_router, prefix="/comments", tags=["Comentarios"])
app.include_router(friendship_router, prefix="/friendship", tags=["Amistades"])
app.include_router(saved_event_router, prefix="/saved-events", tags=["Eventos Guardados"])
app.include_router(agenda_router, prefix="/agenda", tags=["Agenda"])
app.include_router(like_router, prefix="/posts", tags=["Likes"])
app.include_router(notification_router, prefix="/notifications", tags=["Notificaciones"])
app.include_router(upload_router, prefix="/upload", tags=["Subida de Archivos"])
app.include_router(qr_attendance_router, prefix="/qr-attendance", tags=["QR y Asistencia"])
app.include_router(configuracion_router, prefix="/users", tags=["Configuraciones de Usuario"])
