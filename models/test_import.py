try:
    from sqlalchemy.dialects.postgresql import TIMESTAMPTZ
    print("¡ÉXITO! La importación de TIMESTAMPTZ funcionó.")
    print(f"Tipo de dato: {TIMESTAMPTZ}")
except ImportError as e:
    print(f"FALLO: No se pudo importar TIMESTAMPTZ. Error: {e}")
except Exception as e:
    print(f"Ocurrió otro error: {e}")