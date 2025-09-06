# 🚀 Implementación de Configuraciones de Usuario - GeoPlanner Backend

## 📋 Resumen

Se han implementado todas las funcionalidades necesarias para que las configuraciones de usuario del frontend se conecten correctamente con el backend. Esto incluye un modelo de base de datos completo, esquemas Pydantic, endpoints REST API, y scripts de migración.

## 🗂️ Archivos Creados/Modificados

### Nuevos Archivos:
- `models/configuracion_usuario.py` - Modelo de base de datos
- `schemas/configuracion_usuario.py` - Esquemas Pydantic
- `routes/configuracion_usuario.py` - Endpoints de la API
- `create_configuracion_table.py` - Script de migración
- `test_configuracion_endpoints.py` - Script de pruebas

### Archivos Modificados:
- `models/usuario.py` - Agregada relación con configuraciones
- `models/__init__.py` - Importado nuevo modelo
- `app.py` - Registradas nuevas rutas
- `requirements.txt` - Agregadas dependencias para QR codes

## 🔧 Instalación y Configuración

### 1. Instalar Dependencias
```bash
pip install qrcode[pil]==7.4.2 Pillow==10.4.0
```

### 2. Crear la Tabla de Configuraciones
```bash
python create_configuracion_table.py
```

### 3. Reiniciar el Servidor
```bash
uvicorn app:app --reload
```

## 📡 Endpoints Implementados

### Configuraciones de Usuario
- `GET /users/settings` - Obtener configuraciones
- `PUT /users/settings` - Actualizar configuraciones

### Seguridad
- `POST /users/change-password` - Cambiar contraseña
- `POST /users/setup-2fa` - Configurar autenticación de dos factores
- `POST /users/verify-2fa` - Verificar código 2FA
- `GET /users/sessions` - Obtener sesiones activas

### Datos y Privacidad
- `POST /users/download-data` - Descargar datos del usuario
- `DELETE /users/delete-account` - Eliminar cuenta
- `GET /users/activity-history` - Historial de actividad

## 🧪 Pruebas

### Ejecutar Pruebas Automáticas
```bash
python test_configuracion_endpoints.py
```

### Pruebas Manuales con curl

#### Obtener Configuraciones
```bash
curl -X GET "http://localhost:8000/users/settings" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Actualizar Configuraciones
```bash
curl -X PUT "http://localhost:8000/users/settings" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "emailNotifications": false,
    "language": "en",
    "contentFilter": "strict"
  }'
```

#### Cambiar Contraseña
```bash
curl -X POST "http://localhost:8000/users/change-password" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldpass",
    "new_password": "newpass"
  }'
```

## 🗄️ Estructura de la Base de Datos

### Tabla: `configuraciones_usuario`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | UUID | Clave primaria |
| `id_usuario` | UUID | Referencia al usuario |
| `email_notifications` | BOOLEAN | Notificaciones por email |
| `push_notifications` | BOOLEAN | Notificaciones push |
| `new_friend_requests` | BOOLEAN | Solicitudes de amistad |
| `event_invitations` | BOOLEAN | Invitaciones a eventos |
| `likes_and_comments` | BOOLEAN | Likes y comentarios |
| `mentions` | BOOLEAN | Menciones |
| `nearby_events` | BOOLEAN | Eventos cercanos |
| `weekly_digest` | BOOLEAN | Resumen semanal |
| `profile_visibility` | VARCHAR(20) | Visibilidad del perfil |
| `show_location` | BOOLEAN | Mostrar ubicación |
| `show_birth_date` | BOOLEAN | Mostrar fecha de nacimiento |
| `allow_friend_requests` | BOOLEAN | Permitir solicitudes |
| `allow_messages` | BOOLEAN | Permitir mensajes |
| `show_online_status` | BOOLEAN | Mostrar estado online |
| `allow_tagging` | BOOLEAN | Permitir etiquetado |
| `two_factor_auth` | BOOLEAN | Autenticación de dos factores |
| `login_alerts` | BOOLEAN | Alertas de inicio de sesión |
| `device_management` | BOOLEAN | Gestión de dispositivos |
| `language` | VARCHAR(10) | Idioma |
| `timezone` | VARCHAR(50) | Zona horaria |
| `content_filter` | VARCHAR(20) | Filtro de contenido |
| `auto_play_videos` | BOOLEAN | Reproducción automática |
| `show_trending_content` | BOOLEAN | Contenido trending |
| `data_usage` | VARCHAR(20) | Uso de datos |
| `analytics_sharing` | BOOLEAN | Compartir analytics |
| `personalized_ads` | BOOLEAN | Anuncios personalizados |
| `fecha_creacion` | TIMESTAMP | Fecha de creación |
| `fecha_actualizacion` | TIMESTAMP | Fecha de actualización |

## 🔐 Características de Seguridad

### Autenticación de Dos Factores (2FA)
- Generación de códigos QR para apps como Google Authenticator
- Códigos de respaldo para recuperación
- Verificación de códigos TOTP
- Almacenamiento seguro de claves secretas

### Gestión de Sesiones
- Seguimiento de sesiones activas
- Información de dispositivo e IP
- Capacidad de cerrar sesiones específicas
- Revocación de todas las sesiones excepto la actual

### Protección de Datos
- Descarga de datos personales (GDPR compliance)
- Eliminación segura de cuentas
- Historial de actividad del usuario
- Encriptación de contraseñas con bcrypt

## 🎯 Integración con Frontend

### Configuraciones por Defecto
El backend proporciona configuraciones por defecto que coinciden con las del frontend:

```python
def get_default_settings():
    return {
        "emailNotifications": True,
        "pushNotifications": True,
        "newFriendRequests": True,
        "eventInvitations": True,
        "likesAndComments": True,
        "mentions": True,
        "nearbyEvents": False,
        "weeklyDigest": True,
        "profileVisibility": "public",
        "showLocation": True,
        "showBirthDate": True,
        "allowFriendRequests": True,
        "allowMessages": True,
        "showOnlineStatus": True,
        "allowTagging": True,
        "twoFactorAuth": False,
        "loginAlerts": True,
        "deviceManagement": True,
        "language": "es",
        "timezone": "America/Caracas",
        "contentFilter": "moderate",
        "autoPlayVideos": True,
        "showTrendingContent": True,
        "dataUsage": "standard",
        "analyticsSharing": True,
        "personalizedAds": False
    }
```

### Respuestas de la API
Todas las respuestas siguen el formato esperado por el frontend:

```json
{
  "mensaje": "Operación exitosa",
  "configuraciones": {
    // ... configuraciones actualizadas
  }
}
```

## 🚨 Consideraciones Importantes

### 1. Migración de Datos
- El script `create_configuracion_table.py` crea configuraciones por defecto para usuarios existentes
- No se pierden datos durante la migración

### 2. Seguridad
- Todas las operaciones requieren autenticación
- Las contraseñas se verifican antes de cambios críticos
- Los tokens JWT se validan en cada endpoint

### 3. Rendimiento
- Se han creado índices en campos frecuentemente consultados
- Las consultas están optimizadas para evitar N+1 queries

### 4. Escalabilidad
- La estructura permite agregar nuevas configuraciones fácilmente
- Los esquemas Pydantic validan los datos de entrada
- El modelo SQLAlchemy maneja las relaciones automáticamente

## 🔄 Flujo de Trabajo Recomendado

1. **Instalar dependencias** nuevas
2. **Ejecutar script de migración** para crear la tabla
3. **Reiniciar el servidor** para cargar las nuevas rutas
4. **Ejecutar pruebas** para verificar que todo funciona
5. **Probar con el frontend** para confirmar la integración

## 📞 Soporte

Si encuentras algún problema:

1. Revisa los logs del servidor
2. Ejecuta las pruebas automáticas
3. Verifica que la base de datos se creó correctamente
4. Confirma que todas las dependencias están instaladas

---

**¡Las configuraciones de usuario están completamente implementadas y listas para usar! 🎉**
