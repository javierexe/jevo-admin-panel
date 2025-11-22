#!/bin/bash

# Script de inicio rápido con backend mock

echo "🚀 Iniciando Jevo Admin Panel con backend mock..."
echo ""

# Verificar si json-server está instalado
if ! command -v json-server &> /dev/null; then
    echo "❌ json-server no está instalado"
    echo "📦 Instalando json-server globalmente..."
    npm install -g json-server
    echo ""
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    echo "VITE_API_URL=http://localhost:3000" > .env
    echo "VITE_ADMIN_EMAIL=admin@jevo.com" >> .env
    echo "VITE_ADMIN_PASSWORD=admin123" >> .env
    echo "✅ Archivo .env creado"
    echo ""
fi

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar backend mock
echo "🔧 Iniciando backend mock en puerto 3000..."
cd mock-backend
json-server --watch db.json --port 3000 &
BACKEND_PID=$!
cd ..
sleep 2

# Iniciar frontend
echo "🎨 Iniciando frontend en puerto 5173..."
npm run dev &
FRONTEND_PID=$!
sleep 3

echo ""
echo "✅ Todo listo!"
echo ""
echo "📱 Panel Admin: http://localhost:5173"
echo "🔧 Backend Mock: http://localhost:3000"
echo ""
echo "👤 Credenciales:"
echo "   Email: admin@jevo.com"
echo "   Password: admin123"
echo ""
echo "⏸️  Presiona Ctrl+C para detener ambos servidores"
echo ""

# Mantener el script corriendo
wait
