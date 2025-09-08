#!/usr/bin/env python3
"""
Script para probar la configuración de CORS del backend
"""

import requests
import json

def test_cors():
    """Prueba la configuración de CORS del backend"""
    
    backend_url = "https://geoplanner-back.onrender.com"
    frontend_origin = "https://geoplanner-0uva.onrender.com"
    
    print("🔍 Probando configuración de CORS...")
    print(f"Backend: {backend_url}")
    print(f"Frontend: {frontend_origin}")
    print("-" * 50)
    
    # Headers que simulan una petición desde el frontend
    headers = {
        'Origin': frontend_origin,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }
    
    # Probar endpoint raíz
    try:
        print("1. Probando endpoint raíz...")
        response = requests.get(f"{backend_url}/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("   ✅ CORS configurado correctamente")
        else:
            print("   ❌ CORS no configurado")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 50)
    
    # Probar endpoint de verificación de usuario
    try:
        print("2. Probando endpoint de verificación de usuario...")
        test_username = "testuser123"
        response = requests.get(
            f"{backend_url}/users/check-username/{test_username}", 
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("   ✅ CORS configurado correctamente")
        else:
            print("   ❌ CORS no configurado")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 50)
    
    # Probar endpoint de verificación de email
    try:
        print("3. Probando endpoint de verificación de email...")
        test_email = "test@example.com"
        response = requests.get(
            f"{backend_url}/users/check-email/{test_email}", 
            headers=headers
        )
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("   ✅ CORS configurado correctamente")
        else:
            print("   ❌ CORS no configurado")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("-" * 50)
    print("🏁 Prueba completada")

if __name__ == "__main__":
    test_cors()
