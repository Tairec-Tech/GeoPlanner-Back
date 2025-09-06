#!/usr/bin/env python3
"""
Script para crear la tabla de configuraciones de usuario
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal
from models.configuracion_usuario import ConfiguracionUsuario
from models.usuario import Usuario
from sqlalchemy import text

def create_configuracion_table():
    """Crea la tabla de configuraciones de usuario"""
    
    # SQL para crear la tabla
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS configuraciones_usuario (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        id_usuario UUID NOT NULL UNIQUE REFERENCES usuarios(id) ON DELETE CASCADE,
        
        -- Notificaciones
        email_notifications BOOLEAN DEFAULT TRUE,
        push_notifications BOOLEAN DEFAULT TRUE,
        new_friend_requests BOOLEAN DEFAULT TRUE,
        event_invitations BOOLEAN DEFAULT TRUE,
        likes_and_comments BOOLEAN DEFAULT TRUE,
        mentions BOOLEAN DEFAULT TRUE,
        nearby_events BOOLEAN DEFAULT FALSE,
        weekly_digest BOOLEAN DEFAULT TRUE,
        
        -- Privacidad
        profile_visibility VARCHAR(20) DEFAULT 'public',
        show_location BOOLEAN DEFAULT TRUE,
        show_birth_date BOOLEAN DEFAULT TRUE,
        allow_friend_requests BOOLEAN DEFAULT TRUE,
        allow_messages BOOLEAN DEFAULT TRUE,
        show_online_status BOOLEAN DEFAULT TRUE,
        allow_tagging BOOLEAN DEFAULT TRUE,
        
        -- Seguridad
        two_factor_auth BOOLEAN DEFAULT FALSE,
        login_alerts BOOLEAN DEFAULT TRUE,
        device_management BOOLEAN DEFAULT TRUE,
        
        -- Contenido
        language VARCHAR(10) DEFAULT 'es',
        timezone VARCHAR(50) DEFAULT 'America/Caracas',
        content_filter VARCHAR(20) DEFAULT 'moderate',
        auto_play_videos BOOLEAN DEFAULT TRUE,
        show_trending_content BOOLEAN DEFAULT TRUE,
        
        -- Datos
        data_usage VARCHAR(20) DEFAULT 'standard',
        analytics_sharing BOOLEAN DEFAULT TRUE,
        personalized_ads BOOLEAN DEFAULT FALSE,
        
        -- Metadatos
        fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Crear índices para mejorar el rendimiento
    CREATE INDEX IF NOT EXISTS idx_configuracion_usuario_id ON configuraciones_usuario(id_usuario);
    CREATE INDEX IF NOT EXISTS idx_configuracion_profile_visibility ON configuraciones_usuario(profile_visibility);
    CREATE INDEX IF NOT EXISTS idx_configuracion_two_factor ON configuraciones_usuario(two_factor_auth);
    """
    
    try:
        with engine.connect() as conn:
            # Ejecutar la creación de la tabla
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ Tabla de configuraciones de usuario creada exitosamente")
            
            # Crear configuraciones por defecto para usuarios existentes
            db = SessionLocal()
            try:
                # Obtener todos los usuarios que no tienen configuraciones
                usuarios_sin_config = db.query(Usuario).outerjoin(
                    ConfiguracionUsuario, Usuario.id == ConfiguracionUsuario.id_usuario
                ).filter(ConfiguracionUsuario.id_usuario.is_(None)).all()
                
                if usuarios_sin_config:
                    print(f"📝 Creando configuraciones por defecto para {len(usuarios_sin_config)} usuarios...")
                    
                    for usuario in usuarios_sin_config:
                        config = ConfiguracionUsuario(
                            id_usuario=usuario.id,
                            # Las configuraciones por defecto ya están definidas en el modelo
                        )
                        db.add(config)
                    
                    db.commit()
                    print(f"✅ Configuraciones por defecto creadas para {len(usuarios_sin_config)} usuarios")
                else:
                    print("ℹ️  Todos los usuarios ya tienen configuraciones")
                    
            except Exception as e:
                db.rollback()
                print(f"❌ Error creando configuraciones por defecto: {e}")
            finally:
                db.close()
                
    except Exception as e:
        print(f"❌ Error creando la tabla: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando creación de tabla de configuraciones de usuario...")
    success = create_configuracion_table()
    if success:
        print("🎉 Proceso completado exitosamente")
    else:
        print("💥 Error en el proceso")
        sys.exit(1)
