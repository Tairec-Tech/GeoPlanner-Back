import os
from dotenv import load_dotenv

#Cargar nuestras variables de entorno
load_dotenv()

#Definimos todas las variables ocn datos sensibles de nuestra app
config = {
    'DB_USER': os.getenv('DB_USER', None),
    'DB_PASSWORD': os.getenv('DB_PASSWORD', None),
    'DB_HOST': os.getenv('DB_HOST', None),
    'DB_NAME': os.getenv('DB_NAME', None),
}