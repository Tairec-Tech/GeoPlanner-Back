#!/usr/bin/env python3
"""
Script de configuración inicial para GeoPlanner Backend
"""

import os
import subprocess
import sys
from pathlib import Path

def create_env_file():
    """Crear archivo .env con configuración por defecto"""
    env_content = """# Configuración de Base de Datos PostgreSQL
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_NAME=geoplanner_social

# Configuración JWT
SECRET_KEY=tu_clave_secreta_muy_segura_aqui_cambiala_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Configuración del servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True
"""
    
    env_path = Path('.env')
    if not env_path.exists():
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Archivo .env creado con configuración por defecto")
    else:
        print("⚠️  El archivo .env ya existe")

def install_dependencies():
    """Instalar dependencias del proyecto"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar dependencias")
        return False
    return True

def run_migrations():
    """Ejecutar migraciones de la base de datos"""
    try:
        subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], check=True)
        print("✅ Migraciones ejecutadas correctamente")
    except subprocess.CalledProcessError:
        print("❌ Error al ejecutar migraciones")
        return False
    return True

def main():
    """Función principal del script de configuración"""
    print("🚀 Configurando GeoPlanner Backend...")
    print("=" * 50)
    
    # Crear archivo .env
    create_env_file()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ No se pudieron instalar las dependencias")
        return
    
    # Ejecutar migraciones
    if not run_migrations():
        print("❌ No se pudieron ejecutar las migraciones")
        print("💡 Asegúrate de que PostgreSQL esté ejecutándose y configurado correctamente")
        return
    
    print("=" * 50)
    print("✅ Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Configura las variables en el archivo .env según tu entorno")
    print("2. Ejecuta el servidor con: python run.py")
    print("3. Accede a la documentación en: http://localhost:8000/docs")
    print("\n🐳 O usa Docker Compose:")
    print("docker-compose up --build")

if __name__ == "__main__":
    main() 