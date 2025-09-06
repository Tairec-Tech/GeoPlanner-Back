# Importar librerias necesarias para establecer conexion FastAPI + PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Configuracion de la aplicacion
from config import config

# Lógica para verificar si la base de datos existe y crearla si no es así
def create_database_if_not_exists():
    # Solo ejecutar en desarrollo local, no en Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("Ejecutando en Railway - saltando creación de base de datos")
        return
    
    # Importar libreria de conexion python + postgres
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            dbname='postgres',
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            host=config['DB_HOST']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Verificar si la base de datos ya existe
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config['DB_NAME']}'")
        exists = cursor.fetchone()

        if not exists:
            # Crear la base de datos si no existe, con codificación UTF8
            cursor.execute(f"CREATE DATABASE {config['DB_NAME']} ENCODING 'UTF8'")

        # Cerrar la conexion
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al conectar o crear la base de datos: {e}")

# Ejecutar la funcion para crear la base de datos si no existe
create_database_if_not_exists()

# String que conecta SQLAlchemy con PostgreSQL
# Usar DATABASE_URL de Railway si está disponible, sino construir la URL
if config.get('DATABASE_URL'):
    DATABASE_URL = config['DATABASE_URL']
else:
    DATABASE_URL = f'postgresql+psycopg2://{config["DB_USER"]}:{config["DB_PASSWORD"]}@{config["DB_HOST"]}/{config["DB_NAME"]}'

# Crear motor de conexion de PostgreSQL
engine = create_engine(DATABASE_URL)

# Crear tienda de sesiones de conexion con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para todos nuestros modelos (tablas) de base de datos 
Base = declarative_base()

# Funcion que retorna una instancia de conexion con la base de datos
def get_db():
    db = SessionLocal()
    try:
        # Generamos una sesion de conexion con base de datos
        yield db
    finally:
        # Cerramos la conexion con bases de datos para liberar memoria
        db.close()