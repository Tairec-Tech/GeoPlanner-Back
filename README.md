# GeoPlanner Backend

Backend de la red social GeoPlanner desarrollado con FastAPI y PostgreSQL.

## 🚀 Características

- **Autenticación JWT**: Sistema de autenticación seguro con tokens JWT
- **Gestión de Usuarios**: Registro, login y gestión de perfiles de usuario
- **Publicaciones**: Sistema de posts con likes y comentarios
- **Sistema de Amistades**: Gestión de relaciones entre usuarios
- **Agenda Personal**: Gestión de actividades y eventos personales
- **Eventos Guardados**: Sistema para guardar eventos favoritos
- **Geolocalización**: Soporte para ubicaciones de usuarios
- **Base de Datos PostgreSQL**: Base de datos robusta y escalable

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL
- pip

## 🛠️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd Geoplanner-Back
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   - Instalar PostgreSQL
   - Crear una base de datos llamada `geoplanner_social`
   - Configurar las credenciales en el archivo `.env`

5. **Crear archivo .env**
   ```bash
   # Copiar el archivo de ejemplo
   cp .env.example .env
   # Editar con tus credenciales
   ```

6. **Ejecutar migraciones**
   ```bash
   alembic upgrade head
   ```

## 🚀 Ejecutar el Servidor

### Opción 1: Usando run.py
```bash
python run.py
```

### Opción 2: Usando uvicorn directamente
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📚 Documentación de la API

Una vez ejecutado el servidor, puedes acceder a:

- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base de Datos
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_NAME=geoplanner_social

# JWT
SECRET_KEY=tu_clave_secreta_muy_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 📁 Estructura del Proyecto

```
Geoplanner-Back/
├── alembic/                 # Migraciones de base de datos
├── auth/                    # Autenticación
├── config/                  # Configuración
├── database/                # Configuración de base de datos
├── models/                  # Modelos de SQLAlchemy
├── routes/                  # Rutas de la API
├── schemas/                 # Esquemas Pydantic
├── services/                # Lógica de negocio
├── app.py                   # Aplicación principal
├── run.py                   # Script de ejecución
└── requirements.txt         # Dependencias
```

## 🔌 Endpoints Principales

### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión
- `POST /auth/token` - Obtener token JWT

### Usuarios
- `GET /users/me` - Obtener perfil actual
- `PUT /users/me` - Actualizar perfil
- `GET /users/{user_id}` - Obtener perfil de usuario

### Publicaciones
- `GET /posts` - Listar publicaciones
- `POST /posts` - Crear publicación
- `GET /posts/{post_id}` - Obtener publicación
- `PUT /posts/{post_id}` - Actualizar publicación
- `DELETE /posts/{post_id}` - Eliminar publicación

### Comentarios
- `GET /comments` - Listar comentarios
- `POST /comments` - Crear comentario
- `PUT /comments/{comment_id}` - Actualizar comentario
- `DELETE /comments/{comment_id}` - Eliminar comentario

### Amistades
- `GET /friendships` - Listar amistades
- `POST /friendships` - Enviar solicitud de amistad
- `PUT /friendships/{friendship_id}` - Aceptar/rechazar amistad
- `DELETE /friendships/{friendship_id}` - Eliminar amistad

### Agenda
- `GET /agenda` - Listar actividades de agenda
- `POST /agenda` - Crear actividad
- `PUT /agenda/{activity_id}` - Actualizar actividad
- `DELETE /agenda/{activity_id}` - Eliminar actividad

### Eventos Guardados
- `GET /saved-events` - Listar eventos guardados
- `POST /saved-events` - Guardar evento
- `DELETE /saved-events/{event_id}` - Eliminar evento guardado

## 🛡️ Seguridad

- Autenticación JWT
- Contraseñas hasheadas con bcrypt
- Validación de datos con Pydantic
- CORS configurado
- Manejo de excepciones global

## 🧪 Testing

Para ejecutar las pruebas:
```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar pruebas
pytest
```

## 📦 Despliegue

### Docker (Recomendado)
```bash
# Construir imagen
docker build -t geoplanner-backend .

# Ejecutar contenedor
docker run -p 8000:8000 geoplanner-backend
```

### Producción
1. Configurar variables de entorno para producción
2. Usar un servidor WSGI como Gunicorn
3. Configurar un proxy reverso (nginx)
4. Configurar SSL/TLS

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico, contacta a:
- Email: soporte@geoplanner.com
- Issues: [GitHub Issues](https://github.com/tu-usuario/geoplanner-backend/issues) 