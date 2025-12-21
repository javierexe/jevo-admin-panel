# Mock Backend para Desarrollo

Este directorio contiene un servidor mock usando json-server para desarrollo local.

## Instalación

```bash
npm install -g json-server
```

## Uso

Desde el directorio raíz del proyecto:

```bash
cd mock-backend
json-server --watch db.json --port 3000
```

El servidor estará disponible en `http://localhost:3000`

## Endpoints Disponibles

- `GET http://localhost:3000/incidents` - Lista todos los incidentes
- `GET http://localhost:3000/incidents/:id` - Obtiene un incidente específico
- `PATCH http://localhost:3000/incidents/:id` - Actualiza un incidente
- `POST http://localhost:3000/incidents` - Crea un nuevo incidente
- `DELETE http://localhost:3000/incidents/:id` - Elimina un incidente

## Configuración del Frontend

1. Crea un archivo `.env` en la raíz del proyecto:
   ```
   VITE_API_URL=http://localhost:3000
   ```

2. Inicia el servidor mock:
   ```bash
   cd mock-backend
   json-server --watch db.json --port 3000
   ```

3. En otra terminal, inicia el frontend:
   ```bash
   npm run dev
   ```

## Ejemplo de Prueba

```bash
# Listar incidentes
curl http://localhost:3000/incidents

# Obtener incidente #1
curl http://localhost:3000/incidents/1

# Actualizar estado
curl -X PATCH http://localhost:3000/incidents/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in-progress"}'

# Agregar comentario
curl -X PATCH http://localhost:3000/incidents/1 \
  -H "Content-Type: application/json" \
  -d '{"comments": "Trabajando en la solución"}'
```

## Notas

- Los datos se persisten en `db.json`
- Reinicia el servidor para recargar los datos originales
- json-server simula automáticamente delays de red (~200ms)
