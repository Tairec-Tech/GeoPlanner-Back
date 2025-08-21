from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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

# Crear tablas automáticamente
Base.metadata.create_all(engine)

# Instancia principal de la aplicación
app = FastAPI(
    title="GeoPlanner API",
    description="REST API para la red social GeoPlanner",
    version="5.0.0"
)

# Lista de orígenes permitidos (de dónde puede venir la solicitud)
# Para desarrollo, puedes permitir el origen de tu app de React.
# Si usas Vite, suele ser 'http://localhost:5173'.
origins = [
    "http://localhost:5173",
    "http://localhost:3000", # Si usas Create React App
    # Añade aquí la URL de tu frontend si está en producción
]

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Endpoint de prueba para verificar autenticación
@app.get("/test-auth")
def test_auth():
    return {"mensaje": "Endpoint de prueba sin autenticación funcionando"}

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
