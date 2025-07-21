# Importar librerías necesarias
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg # Librería para PostgreSQL v3

# Importar configuración de la aplicación
from config import config

# String de conexión para SQLAlchemy con psycopg3
DATABASE_URL = f"postgresql+psycopg://{config['DB_USER']}:{config['DB_PASSWORD']}@{config['DB_HOST']}/{config['DB_NAME']}"

# -----------------------------------------------------------------
# ## INICIO DE LA LÓGICA DE CREACIÓN AUTOMÁTICA DE BASE DE DATOS ##
# -----------------------------------------------------------------

try:
    # 1. Intento inicial de crear el motor de conexión.
    #    SQLAlchemy no crea la base de datos aquí, solo se prepara para conectar.
    engine = create_engine(DATABASE_URL)

    # 2. Se intenta establecer una conexión real para verificar si la DB existe.
    #    Si la base de datos no existe, esta línea lanzará una excepción.
    with engine.connect() as connection:
        print(f"Conexión exitosa a la base de datos '{config['DB_NAME']}'.")
        pass

# 3. Si la conexión falla (porque la DB no existe), se captura el error.
except Exception as e:
    print(f"La base de datos '{config['DB_NAME']}' no existe. Intentando crearla...")
    
    try:
        # 4. Conexión a la base de datos "postgres" por defecto (esta siempre existe).
        #    Esta conexión es necesaria para tener permisos y poder ejecutar CREATE DATABASE.
        #    'autocommit=True' es crucial para que el comando CREATE DATABASE se ejecute fuera de una transacción.
        conn = psycopg.connect(
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            host=config['DB_HOST'],
            dbname='postgres', # Conectar a la base de datos de mantenimiento
            autocommit=True
        )

        # 5. Ejecutar el comando SQL para crear la nueva base de datos.
        #    Se usa f-string de forma segura porque el nombre de la DB viene de tu archivo de config.
        #    Si fuera un input de usuario, se debería sanitizar.
        conn.execute(f'CREATE DATABASE "{config["DB_NAME"]}"')
        
        print(f"Base de datos '{config['DB_NAME']}' creada exitosamente.")

        # Cerrar la conexión de mantenimiento
        conn.close()

        # 6. Ahora que la base de datos ya existe, se crea el motor de SQLAlchemy
        #    definitivo que usará el resto de la aplicación.
        engine = create_engine(DATABASE_URL)

    except Exception as create_error:
        print(f"ERROR: No se pudo crear la base de datos. Revisa los permisos del usuario.")
        print(f"Detalle del error: {create_error}")
        raise create_error

# ---------------------------------------------------------------
# ## FIN DE LA LÓGICA DE CREACIÓN AUTOMÁTICA ##
# ---------------------------------------------------------------

# Crear la fábrica de sesiones (SessionLocal) para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base para los modelos ORM de SQLAlchemy
Base = declarative_base()


# Función de dependencia para las rutas de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()