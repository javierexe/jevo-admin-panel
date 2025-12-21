# JEVO Incidents Backend API

Backend completo en FastAPI + PostgreSQL para un servicio centralizado de reportes de incidentes.

## 🚀 Características

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional con SQLAlchemy 2.x
- **Alembic** - Migraciones de base de datos
- **JWT Authentication** - Autenticación segura con tokens
- **File Upload** - Soporte para Cloudinary y almacenamiento local
- **CORS** - Configurado para JEVO Admin Panel
- **Documentación automática** - Swagger UI y ReDoc

## 📋 Requisitos Previos

- Python 3.9+
- PostgreSQL 13+
- (Opcional) Cuenta de Cloudinary para almacenamiento en la nube

## 🛠️ Instalación

### 1. Clonar el repositorio o navegar al directorio backend

```bash
cd backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos PostgreSQL

Crear una base de datos PostgreSQL:

```sql
CREATE DATABASE jevo_incidents;
```

### 5. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y actualizar las variables:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/jevo_incidents
JWT_SECRET=tu-clave-secreta-muy-segura
UPLOAD_STORAGE=local  # o 'cloudinary'
```

Si usas Cloudinary, agregar también:

```env
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret
```

### 6. Ejecutar migraciones

```bash
alembic upgrade head
```

## 🚀 Iniciar el Backend

### Modo Desarrollo

Usando el script proporcionado:

```bash
chmod +x start-dev.sh
./start-dev.sh
```

O directamente con uvicorn:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

### Documentación de la API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Estructura del Proyecto

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py          # Endpoints de autenticación
│   │   └── incidents.py     # Endpoints de incidentes
│   ├── core/
│   │   ├── config.py        # Configuración de la aplicación
│   │   ├── database.py      # Conexión a la base de datos
│   │   └── security.py      # JWT y autenticación
│   ├── models/
│   │   ├── incident.py      # Modelo de incidentes
│   │   └── user.py          # Modelo de usuarios
│   ├── schemas/
│   │   ├── incident.py      # Schemas Pydantic para incidentes
│   │   └── user.py          # Schemas Pydantic para usuarios
│   ├── services/
│   │   └── upload.py        # Servicio de carga de archivos
│   └── main.py              # Aplicación principal
├── alembic/
│   ├── versions/            # Migraciones de la base de datos
│   └── env.py               # Configuración de Alembic
├── uploads/                 # Archivos subidos (modo local)
├── .env.example             # Ejemplo de variables de entorno
├── .gitignore
├── alembic.ini              # Configuración de Alembic
├── requirements.txt         # Dependencias de Python
├── start-dev.sh             # Script de inicio en desarrollo
└── README.md
```

## 🔐 API Endpoints

### Autenticación

- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión (obtener token JWT)

### Incidentes

- `POST /incidents` - Crear nuevo incidente (con archivos opcionales)
- `GET /incidents` - Listar incidentes (con filtros opcionales)
- `GET /incidents/{id}` - Obtener incidente específico
- `PATCH /incidents/{id}` - Actualizar incidente

## 📝 Modelos de Datos

### User

- `id`: UUID (PK)
- `email`: String (único)
- `password_hash`: String
- `is_active`: Boolean
- `created_at`: DateTime

### Incident

- `id`: UUID (PK)
- `project`: String
- `category`: String
- `description`: Text
- `image_url`: String (opcional)
- `video_url`: String (opcional)
- `status`: String (open, in_progress, resolved)
- `internal_comment`: Text (opcional)
- `created_at`: DateTime
- `resolved_at`: DateTime (opcional)

## 🔧 Configuración

### Almacenamiento de Archivos

El sistema soporta dos métodos de almacenamiento:

1. **Local** (por defecto): Los archivos se guardan en la carpeta `uploads/`
2. **Cloudinary**: Los archivos se suben a Cloudinary

Cambiar en `.env`:

```env
UPLOAD_STORAGE=local  # o 'cloudinary'
```

### CORS

Configurar los orígenes permitidos en `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🧪 Uso de la API

### Ejemplo: Crear un incidente con archivos

```bash
curl -X POST "http://localhost:8000/incidents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "project=Panel Admin" \
  -F "category=Bug" \
  -F "description=Error en el login" \
  -F "status=open" \
  -F "image=@screenshot.png" \
  -F "video=@recording.mp4"
```

### Ejemplo: Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

## 🔄 Migraciones

### Crear una nueva migración

```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

### Revertir una migración

```bash
alembic downgrade -1
```

## 🐛 Solución de Problemas

### Error de conexión a la base de datos

Verificar que PostgreSQL esté ejecutándose y que la URL en `.env` sea correcta.

### Error al importar módulos

Asegurarse de que el entorno virtual esté activado:

```bash
source venv/bin/activate
```

### Error con Cloudinary

Si usas Cloudinary, verificar que todas las credenciales estén configuradas correctamente en `.env`.

## 📦 Dependencias Principales

- `fastapi` - Framework web
- `uvicorn` - Servidor ASGI
- `sqlalchemy` - ORM
- `alembic` - Migraciones
- `psycopg2-binary` - Driver PostgreSQL
- `pydantic` - Validación de datos
- `python-jose` - JWT
- `passlib` - Hashing de contraseñas
- `python-multipart` - Manejo de form-data
- `cloudinary` - Integración con Cloudinary

## 📄 Licencia

Este proyecto es parte del JEVO Admin Panel.

## 👥 Contacto

Para preguntas o soporte, contactar al equipo de desarrollo.
