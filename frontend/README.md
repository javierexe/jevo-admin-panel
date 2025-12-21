# Jevo Admin Panel

Panel administrativo web para gestionar incidentes reportados desde varios proyectos (POS botillería, agenda lava autos, etc.).

## Características

- ✅ Interfaz moderna con tema oscuro
- ✅ Autenticación básica
- ✅ Lista de incidentes con filtros avanzados
- ✅ Vista detallada de cada incidente
- ✅ Gestión de estados (Pendiente, En Progreso, Resuelto)
- ✅ Sistema de comentarios internos
- ✅ Preparado para integración con backend

## Tecnologías

- React 18
- Vite
- Tailwind CSS
- React Router DOM

## Instalación

```bash
# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env

# Iniciar servidor de desarrollo
npm run dev
```

## Credenciales por defecto

- **Email:** admin@jevo.com
- **Contraseña:** admin123

## Estructura del proyecto

```
src/
├── components/         # Componentes reutilizables
│   ├── IncidentDetail.jsx
│   ├── IncidentFilters.jsx
│   ├── IncidentTable.jsx
│   ├── Layout.jsx
│   ├── Login.jsx
│   ├── Navbar.jsx
│   └── ProtectedRoute.jsx
├── context/           # Context API para estado global
│   ├── AuthContext.jsx
│   └── IncidentsContext.jsx
├── data/             # Datos mock
│   └── mockData.js
├── pages/            # Páginas de la aplicación
│   └── Dashboard.jsx
├── utils/            # Utilidades y helpers
│   └── api.js
├── App.jsx
├── main.jsx
└── index.css
```

## Scripts disponibles

```bash
npm run dev      # Inicia servidor de desarrollo
npm run build    # Construye para producción
npm run preview  # Preview de build de producción
```

## Próximos pasos

### Integración con Backend

El panel ya está completamente integrado con un backend real. Solo necesitas:

1. **Configurar la URL del backend**
   ```bash
   # Crea un archivo .env basado en .env.example
   cp .env.example .env
   
   # Edita .env y configura la URL de tu backend
   VITE_API_URL=http://localhost:3000/api
   ```

2. **Endpoints requeridos en el backend**
   
   ```
   GET /api/incidents
   Retorna: Array de incidentes
   
   GET /api/incidents/:id
   Retorna: Objeto con detalle del incidente
   
   PATCH /api/incidents/:id
   Body: { status?: string, internalComment?: string }
   Retorna: Incidente actualizado
   ```

3. **Estructura de datos esperada**
   
   ```json
   {
     "id": 1,
     "project": "POS Botillería",
     "category": "Error crítico",
     "status": "pending",
     "description": "Breve descripción",
     "fullDescription": "Descripción completa del incidente",
     "date": "2024-01-15T10:30:00Z",
     "image": "https://example.com/image.jpg",
     "comments": "Comentarios internos"
   }
   ```

### Servicios API disponibles

El panel incluye un servicio completo en `src/api/incidents.js`:

- `getIncidents()` - Obtiene todos los incidentes
- `getIncidentById(id)` - Obtiene un incidente específico
- `updateIncident(id, payload)` - Actualiza un incidente

### Estados de carga y errores

El panel maneja automáticamente:
- ✅ Loading states durante las peticiones
- ✅ Error handling con mensajes al usuario
- ✅ Refresh automático después de actualizar incidentes
- ✅ Fallbacks en caso de error de conexión

## Personalización

### Colores del tema oscuro

Edita `tailwind.config.js` para personalizar los colores:

```js
colors: {
  dark: {
    bg: '#1d1f21',        // Fondo principal
    card: '#2a2d31',      // Tarjetas/Cards
    border: '#3a3d41',    // Bordes
    text: '#e4e6eb',      // Texto principal
    'text-secondary': '#b0b3b8', // Texto secundario
  }
}
```

## Licencia

Proyecto privado - Jevo
