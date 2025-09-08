# 🔧 Guía de Solución de Problemas CORS - GeoPlanner Backend

## ❌ Problema Identificado

El frontend en `https://geoplanner-0uva.onrender.com` no puede conectarse al backend debido a errores de CORS:

```
Access to fetch at 'https://geoplanner-back.onrender.com/users/check-username/Aura1' 
from origin 'https://geoplanner-0uva.onrender.com' has been blocked by CORS policy: 
Response to preflight request doesn't pass access control check: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## ✅ Solución Implementada

### 1. Actualización de Orígenes Permitidos

**Archivo modificado**: `app.py` (líneas 45-54)

**Cambios realizados**:
```python
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "https://geoplanner-front.vercel.app",
    "https://geoplanner.vercel.app",
    "https://geoplanner-0uva.onrender.com",  # ✅ NUEVO: Tu frontend en Render
    "https://*.onrender.com",  # ✅ NUEVO: Permitir cualquier subdominio de Render
]
```

### 2. Mejora de Configuración CORS

**Archivo modificado**: `app.py` (líneas 57-64)

**Cambios realizados**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # ✅ Mejorado
    allow_headers=["*"],
    expose_headers=["*"],  # ✅ NUEVO: Exponer headers
)
```

## 🚀 Pasos para Aplicar la Solución

### 1. Desplegar Cambios en Render

1. **Sube los cambios al repositorio**:
   ```bash
   git add .
   git commit -m "Fix CORS configuration for Render frontend"
   git push origin main
   ```

2. **Render detectará automáticamente los cambios** y redesplegará el backend.

3. **Espera 2-3 minutos** para que el despliegue se complete.

### 2. Verificar que el Backend Esté Funcionando

1. **Prueba el endpoint raíz**:
   ```
   https://geoplanner-back.onrender.com/
   ```
   Debería devolver:
   ```json
   {
     "mensaje": "Bienvenido a GeoPlanner API",
     "version": "5.0.0",
     "estado": "activo"
   }
   ```

2. **Prueba con curl** (opcional):
   ```bash
   curl -H "Origin: https://geoplanner-0uva.onrender.com" \
        -H "Access-Control-Request-Method: GET" \
        -H "Access-Control-Request-Headers: Content-Type" \
        -X OPTIONS \
        https://geoplanner-back.onrender.com/users/check-username/test
   ```

### 3. Verificar en el Frontend

1. **Abre tu frontend**: `https://geoplanner-0uva.onrender.com`

2. **Abre las herramientas de desarrollador** (F12)

3. **Ve a la pestaña Network**

4. **Intenta registrar un usuario** y verifica que:
   - Las peticiones van a `https://geoplanner-back.onrender.com`
   - No hay errores de CORS
   - Las respuestas incluyen headers de CORS

## 🔍 Verificación de Headers CORS

Después del despliegue, las respuestas del backend deberían incluir estos headers:

```
Access-Control-Allow-Origin: https://geoplanner-0uva.onrender.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: *
Access-Control-Allow-Credentials: true
```

## 🐛 Solución de Problemas Adicionales

### Si el problema persiste:

1. **Verifica que el backend se haya redesplegado**:
   - Ve al dashboard de Render
   - Confirma que el último despliegue fue exitoso
   - Revisa los logs para errores

2. **Limpia la caché del navegador**:
   - Ctrl + Shift + R (hard refresh)
   - O abre una ventana de incógnito

3. **Verifica la URL del frontend**:
   - Confirma que sea exactamente `https://geoplanner-0uva.onrender.com`
   - Sin trailing slash

### Si necesitas agregar más orígenes:

Edita el archivo `app.py` y agrega la nueva URL a la lista `origins`:

```python
origins = [
    # ... URLs existentes ...
    "https://tu-nueva-url.com",  # Nueva URL
]
```

## 📋 Checklist de Verificación

- [ ] Cambios subidos al repositorio
- [ ] Backend redesplegado en Render
- [ ] Endpoint raíz responde correctamente
- [ ] Headers CORS presentes en las respuestas
- [ ] Frontend puede hacer peticiones sin errores CORS
- [ ] Registro de usuarios funciona
- [ ] Login funciona
- [ ] Todas las funcionalidades principales operativas

## 🎯 Resultado Esperado

Después de aplicar estos cambios:

1. ✅ El frontend podrá conectarse al backend sin errores CORS
2. ✅ Las peticiones de verificación de usuario/email funcionarán
3. ✅ El registro de usuarios funcionará correctamente
4. ✅ Todas las funcionalidades de la API estarán disponibles

---

**Tiempo estimado para la solución**: 5-10 minutos (incluyendo tiempo de despliegue)

**Nota**: Los cambios son inmediatos una vez que Render complete el redespliegue.
