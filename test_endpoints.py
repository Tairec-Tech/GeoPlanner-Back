import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("🧪 Probando endpoints de perfiles públicos...")
    
    # 1. Probar endpoint de documentación
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Documentación accesible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo a documentación: {e}")
        return
    
    # 2. Probar endpoint de usuarios (sin autenticación)
    try:
        response = requests.get(f"{BASE_URL}/users/all")
        print(f"📊 Endpoint /users/all: {response.status_code}")
        if response.status_code == 401:
            print("   (Esperado - requiere autenticación)")
        elif response.status_code == 200:
            users = response.json()
            print(f"   Usuarios encontrados: {len(users)}")
            if users:
                test_user_id = users[0]['id']
                print(f"   Usuario de prueba: {test_user_id}")
                
                # 3. Probar endpoint de usuario específico
                response = requests.get(f"{BASE_URL}/users/{test_user_id}")
                print(f"👤 Endpoint /users/{test_user_id}: {response.status_code}")
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"   Usuario: {user_data.get('nombre', 'N/A')} {user_data.get('apellido', 'N/A')}")
                
                # 4. Probar endpoint de publicaciones del usuario
                response = requests.get(f"{BASE_URL}/users/{test_user_id}/posts")
                print(f"📝 Endpoint /users/{test_user_id}/posts: {response.status_code}")
                if response.status_code == 200:
                    posts = response.json()
                    print(f"   Publicaciones encontradas: {len(posts)}")
                elif response.status_code == 500:
                    print("   ❌ Error 500 - Revisar logs del servidor")
                    error_detail = response.text
                    print(f"   Detalle del error: {error_detail}")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")

if __name__ == "__main__":
    test_endpoints()
