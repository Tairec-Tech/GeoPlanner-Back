import os
from dotenv import load_dotenv

# Cargar nuestras variables de entorno
load_dotenv()

# Definimos todas las variables con datos sensibles de nuestra app
config = {
    'DB_USER': os.getenv('DB_USER', 'postgres'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD', 'password'),
    'DB_HOST': os.getenv('DB_HOST', 'localhost'),
    'DB_NAME': os.getenv('DB_NAME', 'geoplanner_social'),
    'SECRET_KEY': os.getenv('SECRET_KEY', 'supersecretkey'),
    'ALGORITHM': os.getenv('ALGORITHM', 'HS256'),
    'ACCESS_TOKEN_EXPIRE_MINUTES': int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60')),
    'HOST': os.getenv('HOST', '0.0.0.0'),
    'PORT': int(os.getenv('PORT', '8000')),
    'DEBUG': os.getenv('DEBUG', 'True').lower() == 'true'
}