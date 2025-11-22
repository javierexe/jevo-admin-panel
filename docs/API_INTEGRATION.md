# Integración con Backend - API Documentation

## Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
VITE_API_URL=http://localhost:3000/api
```

## Endpoints Requeridos

### 1. Listar Incidentes

**Request:**
```http
GET /api/incidents
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "project": "POS Botillería",
    "category": "Error crítico",
    "status": "pending",
    "description": "Error en el sistema de pagos",
    "fullDescription": "El sistema muestra error 500 al procesar pagos con tarjeta...",
    "date": "2024-01-15T10:30:00Z",
    "image": "https://example.com/screenshots/incident1.jpg",
    "comments": "Se investigó el log del servidor"
  },
  {
    "id": 2,
    "project": "Agenda Lava Autos",
    "category": "Bug visual",
    "status": "in-progress",
    "description": "Calendario no muestra correctamente",
    "fullDescription": "Las citas del calendario aparecen desalineadas en móviles...",
    "date": "2024-01-16T14:20:00Z",
    "image": "https://example.com/screenshots/incident2.jpg",
    "comments": ""
  }
]
```

**Estados posibles:**
- `pending` - Pendiente
- `in-progress` - En Progreso
- `resolved` - Resuelto

---

### 2. Obtener Detalle de Incidente

**Request:**
```http
GET /api/incidents/:id
```

**Response (200 OK):**
```json
{
  "id": 1,
  "project": "POS Botillería",
  "category": "Error crítico",
  "status": "pending",
  "description": "Error en el sistema de pagos",
  "fullDescription": "El sistema muestra error 500 al procesar pagos con tarjeta de crédito. Esto ocurre de forma intermitente.",
  "date": "2024-01-15T10:30:00Z",
  "image": "https://example.com/screenshots/incident1.jpg",
  "comments": "Se investigó el log del servidor. Parece ser un problema con el gateway de pagos."
}
```

**Response (404 Not Found):**
```json
{
  "error": "Incidente no encontrado"
}
```

---

### 3. Actualizar Incidente

**Request:**
```http
PATCH /api/incidents/:id
Content-Type: application/json

{
  "status": "in-progress",
  "internalComment": "Se está trabajando en la solución"
}
```

**Campos opcionales:**
- `status` (string) - Nuevo estado del incidente
- `internalComment` (string) - Comentario interno a agregar

**Response (200 OK):**
```json
{
  "id": 1,
  "project": "POS Botillería",
  "category": "Error crítico",
  "status": "in-progress",
  "description": "Error en el sistema de pagos",
  "fullDescription": "El sistema muestra error 500 al procesar pagos con tarjeta de crédito...",
  "date": "2024-01-15T10:30:00Z",
  "image": "https://example.com/screenshots/incident1.jpg",
  "comments": "Se investigó el log del servidor. Parece ser un problema con el gateway de pagos. Se está trabajando en la solución"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Incidente no encontrado"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Estado inválido. Use: pending, in-progress, resolved"
}
```

---

## Manejo de Errores

El frontend maneja automáticamente los siguientes casos:

### Errores de Red
Si el backend no está disponible:
```
Error al obtener incidentes: Failed to fetch
```

### Errores HTTP
- **404:** Muestra mensaje "Incidente no encontrado"
- **500:** Muestra mensaje de error del servidor
- **Otros:** Muestra el statusText de la respuesta

### Timeout
Considera implementar un timeout en el backend (ej: 30 segundos)

---

## Ejemplo de Implementación Backend (Node.js/Express)

```javascript
// Backend example
app.get('/api/incidents', async (req, res) => {
  try {
    const incidents = await db.incidents.findAll();
    res.json(incidents);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener incidentes' });
  }
});

app.get('/api/incidents/:id', async (req, res) => {
  try {
    const incident = await db.incidents.findById(req.params.id);
    if (!incident) {
      return res.status(404).json({ error: 'Incidente no encontrado' });
    }
    res.json(incident);
  } catch (error) {
    res.status(500).json({ error: 'Error al obtener incidente' });
  }
});

app.patch('/api/incidents/:id', async (req, res) => {
  try {
    const { status, internalComment } = req.body;
    
    const incident = await db.incidents.findById(req.params.id);
    if (!incident) {
      return res.status(404).json({ error: 'Incidente no encontrado' });
    }

    if (status) {
      if (!['pending', 'in-progress', 'resolved'].includes(status)) {
        return res.status(400).json({ 
          error: 'Estado inválido. Use: pending, in-progress, resolved' 
        });
      }
      incident.status = status;
    }

    if (internalComment) {
      incident.comments = incident.comments 
        ? `${incident.comments}\n${internalComment}`
        : internalComment;
    }

    await incident.save();
    res.json(incident);
  } catch (error) {
    res.status(500).json({ error: 'Error al actualizar incidente' });
  }
});
```

---

## Testing

Puedes probar los endpoints con curl:

```bash
# Listar incidentes
curl http://localhost:3000/api/incidents

# Obtener un incidente
curl http://localhost:3000/api/incidents/1

# Actualizar estado
curl -X PATCH http://localhost:3000/api/incidents/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in-progress", "internalComment": "Trabajando en ello"}'
```

O con un servidor mock usando json-server:

```bash
# Instalar json-server
npm install -g json-server

# Crear db.json con datos de ejemplo
# Ejecutar
json-server --watch db.json --port 3000 --routes routes.json
```

---

## Consideraciones de Seguridad

Para producción, considera implementar:

1. **Autenticación:** JWT o sesiones para validar usuarios
2. **CORS:** Configurar correctamente los orígenes permitidos
3. **Rate Limiting:** Prevenir abuso de la API
4. **Validación:** Sanitizar y validar todos los inputs
5. **HTTPS:** Usar conexiones seguras en producción

```javascript
// Ejemplo de headers CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'https://admin.jevo.com');
  res.header('Access-Control-Allow-Methods', 'GET, PATCH');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  next();
});
```
