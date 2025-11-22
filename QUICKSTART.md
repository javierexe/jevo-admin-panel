# 🚀 Inicio Rápido

## Opción 1: Script Automático (Recomendado)

```bash
./start-dev.sh
```

Este script:
- ✅ Verifica e instala json-server si es necesario
- ✅ Crea el archivo .env automáticamente
- ✅ Inicia el backend mock en puerto 3000
- ✅ Inicia el frontend en puerto 5173
- ✅ Ambos servidores se detienen con Ctrl+C

## Opción 2: Inicio Manual

### Backend Mock

```bash
# Terminal 1: Backend
cd mock-backend
json-server --watch db.json --port 3000
```

### Frontend

```bash
# Terminal 2: Frontend
npm run dev
```

## Acceso

- **Panel Admin:** http://localhost:5173
- **Backend API:** http://localhost:3000
- **Credenciales:** 
  - Email: `admin@jevo.com`
  - Password: `admin123`

## Probar la API

```bash
# Ver todos los incidentes
curl http://localhost:3000/incidents

# Ver incidente específico
curl http://localhost:3000/incidents/1

# Actualizar estado
curl -X PATCH http://localhost:3000/incidents/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in-progress"}'
```

## Documentación Completa

- **API:** `docs/API_INTEGRATION.md`
- **Resumen de Cambios:** `docs/BACKEND_INTEGRATION_SUMMARY.md`
- **README General:** `README.md`
