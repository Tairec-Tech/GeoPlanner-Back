from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar Base y engine para crear tablas
from database import Base, engine

# Importar todas las rutas
from routes.users import router as user_router
from routes.auth import router as auth_router
from routes.posts import router as post_router
from routes.comments import router as comment_router
from routes.friendship import router as friendship_router
from routes.saved_event import router as saved_event_router
from routes.agenda import router as agenda_router

# Crear tablas automáticamente
Base.metadata.create_all(engine)

# Instancia principal de la aplicación
app = FastAPI(
    title="GeoPlanner API",
    description="REST API para la red social GeoPlanner",
    version="1.0.0"
)

# Middleware de CORS (opcional, recomendado si vas a consumir la API desde frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los routers
app.include_router(user_router, prefix="/users", tags=["Usuarios"])
app.include_router(auth_router, prefix="/auth", tags=["Autenticación"])
app.include_router(post_router, prefix="/posts", tags=["Publicaciones"])
app.include_router(comment_router, prefix="/comments", tags=["Comentarios"])
app.include_router(friendship_router, prefix="/friendships", tags=["Amistades"])
app.include_router(saved_event_router, prefix="/saved-events", tags=["Eventos Guardados"])
app.include_router(agenda_router, prefix="/agenda", tags=["Agenda Privada"])