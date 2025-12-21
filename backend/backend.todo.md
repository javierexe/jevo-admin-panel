Quiero que generes un backend completo en FastAPI + PostgreSQL para un servicio centralizado de reportes de incidentes, siguiendo esta arquitectura:

Estructura deseada:
/app
  /api
    incidents.py
    auth.py
  /core
    config.py
    database.py
    security.py
  /models
    incident.py
    user.py
  /schemas
    incident.py
    user.py
  /services
    upload.py
  main.py

Requerimientos generales:
- Usar FastAPI
- Conexión a PostgreSQL usando SQLAlchemy 2.x
- Migraciones con Alembic
- JWT para autenticación (login, refresh token opcional)
- Manejo de archivos (imágenes/video) vía Cloudinary o carpeta /uploads (implementa ambos, elegir con variable de entorno)
- CORS permitido para panel JEVO Admin Panel

MODELO incident:
  id: UUID PK
  project: str
  category: str
  description: text
  image_url: str | None
  video_url: str | None
  status: str (open, in_progress, resolved) default 'open'
  internal_comment: text | None
  created_at: datetime
  resolved_at: datetime | None

MODELO user:
  id: UUID PK
  email: str unique
  password_hash: str
  is_active: bool

ENDPOINTS:
/auth/login (POST)
/auth/register (POST, opcional)
/incidents (POST, GET)
/incidents/{id} (GET, PATCH)

Requerimientos específicos:
- POST /incidents recibe form-data con archivos opcionales.
- Guardar archivos usando un servicio en /services/upload.py
- Las operaciones de actualización deben validar existencia del incidente.
- Serializar usando Pydantic v2.
- Generar migración inicial con Alembic.

Extras:
- Crear un archivo .env.example con VITE_API_URL, DATABASE_URL, CLOUDINARY_KEY, JWT_SECRET.
- Crear script "start-dev.sh" para correr: uvicorn app.main:app --reload
- Documentar en README cómo iniciar el backend.

Genera todo el código, sin omitir archivos.

