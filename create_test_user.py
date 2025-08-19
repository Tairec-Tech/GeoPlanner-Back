import requests
import json

def create_test_user():
    """Crear un usuario de prueba en el backend"""
    
    # URL del backend
    base_url = "http://localhost:8000"
    
    # Datos del usuario de prueba
    user_data = {
        "nombre_usuario": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "nombre": "Usuario",
        "apellido": "Prueba",
        "fecha_nacimiento": "1990-01-01"
    }
    
    try:
        # Intentar crear el usuario
        response = requests.post(
            f"{base_url}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Usuario de prueba creado exitosamente!")
            print(f"Email: {user_data['email']}")
            print(f"Username: {user_data['nombre_usuario']}")
            print(f"Contraseña: {user_data['password']}")
            print("\nPuedes iniciar sesión con cualquiera de estos:")
            print(f"- Email: {user_data['email']}")
            print(f"- Username: {user_data['nombre_usuario']}")
        elif response.status_code == 400:
            print("ℹ️ El usuario ya existe")
            print(f"Email: {user_data['email']}")
            print(f"Username: {user_data['nombre_usuario']}")
            print(f"Contraseña: {user_data['password']}")
            print("\nPuedes iniciar sesión con cualquiera de estos:")
            print(f"- Email: {user_data['email']}")
            print(f"- Username: {user_data['nombre_usuario']}")
        else:
            print(f"❌ Error al crear usuario: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al backend")
        print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("Creando usuario de prueba...")
    create_test_user() 