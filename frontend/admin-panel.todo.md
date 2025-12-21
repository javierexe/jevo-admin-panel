Quiero que generes un panel web administrativo para gestionar incidentes reportados desde varios proyectos (POS botillería, agenda lava autos, etc.).

## Requerimientos generales
- Proyecto en React con Vite.
- Estilo simple, moderno y oscuro.
- Autenticación básica por ahora (login con email y contraseña fija en .env).
- Código organizado por componentes.
- Reutilizable para otros proyectos.

## Pantalla principal: Lista de incidentes
- Un layout con barra superior (título + botón logout).
- Tabla con columnas: proyecto, categoría, descripción corta, estado, fecha, acciones.
- Botón “Ver” en cada fila que abre el detalle.
- Filtros arriba: proyecto, categoría, estado y búsqueda.
- Utilizar data mockeada por ahora (array estático).

## Detalle de incidente
- Panel dividido en dos columnas:
  - Izquierda: imagen o video (mock), fecha y proyecto.
  - Derecha: categoría, descripción completa, estado (dropdown), campo comentario interno, botón “Marcar como resuelto”.
- Cambiar estado actualiza el mock local.
- Modal o página aparte, lo que sea más simple.

## Componentes
- IncidentTable.jsx
- IncidentFilters.jsx
- IncidentDetail.jsx
- Navbar.jsx
- Login.jsx
- Layout.jsx

## Estilos
- Utilizar CSS Modules o Tailwind (elige uno y mantén consistencia).
- Tema oscuro: fondo #1d1f21, tarjetas #2a2d31, texto gris claro.

## Resultado esperado
- Crear toda la estructura React + los componentes + los estilos.
- Dejar funciones preparadas para conectar a un backend real en el futuro (fetch placeholders).
- Evitar dependencias innecesarias.

Crea el proyecto completo con los archivos y código listos para ejecutar.
