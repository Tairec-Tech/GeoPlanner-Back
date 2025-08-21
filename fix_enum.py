from database import engine
from sqlalchemy import text

def fix_enum():
    """Actualizar manualmente el enum EstadoAmistadEnum en la base de datos"""
    with engine.connect() as conn:
        try:
            # Agregar el valor 'bloqueada' al enum
            conn.execute(text("ALTER TYPE estadoamistadenum ADD VALUE IF NOT EXISTS 'bloqueada'"))
            conn.commit()
            print("✅ Enum actualizado correctamente")
        except Exception as e:
            print(f"❌ Error actualizando enum: {e}")
            conn.rollback()

if __name__ == "__main__":
    fix_enum()
