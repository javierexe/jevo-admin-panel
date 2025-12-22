#!/usr/bin/env python3
"""
Script para verificar y diagnosticar la URL del Cloud API configurada.
Ayuda a identificar problemas de configuración en el deployment.
"""

import os
import sys
import httpx
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def check_cloud_api_url():
    """Verifica la URL del Cloud API y prueba conectividad básica."""
    
    print("=" * 60)
    print("🔍 Verificación de Cloud API URL")
    print("=" * 60)
    
    # Mostrar la URL configurada
    cloud_api_url = settings.CLOUD_API_URL
    print(f"\n📍 CLOUD_API_URL configurada: {cloud_api_url}")
    
    # Analizar la URL
    if not cloud_api_url:
        print("❌ ERROR: CLOUD_API_URL no está configurada")
        return False
    
    if not cloud_api_url.startswith(("http://", "https://")):
        print("⚠️  WARNING: URL no comienza con http:// o https://")
    
    # Construir endpoints a verificar
    endpoints = [
        "/admin/clients",
        "/admin/fields", 
        "/admin/whatsapp-users"
    ]
    
    print(f"\n🧪 Probando endpoints del Cloud API...")
    
    results = {}
    
    for endpoint in endpoints:
        full_url = f"{cloud_api_url}{endpoint}"
        print(f"\n  Probando: {full_url}")
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # Intentar GET
                response = client.get(full_url)
                status = response.status_code
                
                if status == 200:
                    print(f"    ✅ GET {status}: OK")
                    results[endpoint] = "OK"
                elif status == 401:
                    print(f"    🔐 GET {status}: Unauthorized (esperado sin auth)")
                    results[endpoint] = "OK (auth required)"
                elif status == 404:
                    print(f"    ❌ GET {status}: Not Found - endpoint no existe")
                    results[endpoint] = "NOT_FOUND"
                elif status == 405:
                    print(f"    ⚠️  GET {status}: Method Not Allowed")
                    print(f"        Esto sugiere que el endpoint existe pero no acepta GET")
                    print(f"        Verifica la configuración de rutas en el Cloud API")
                    results[endpoint] = "METHOD_NOT_ALLOWED"
                else:
                    print(f"    ⚠️  GET {status}: Unexpected status")
                    results[endpoint] = f"UNEXPECTED_{status}"
                    
        except httpx.ConnectError as e:
            print(f"    ❌ Error de conexión: {e}")
            results[endpoint] = "CONNECTION_ERROR"
        except httpx.TimeoutException:
            print(f"    ❌ Timeout después de 10s")
            results[endpoint] = "TIMEOUT"
        except Exception as e:
            print(f"    ❌ Error: {type(e).__name__}: {e}")
            results[endpoint] = f"ERROR: {type(e).__name__}"
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 Resumen de Resultados")
    print("=" * 60)
    
    for endpoint, result in results.items():
        emoji = "✅" if result.startswith("OK") else "❌"
        print(f"  {emoji} {endpoint}: {result}")
    
    # Verificar variables de entorno críticas
    print("\n" + "=" * 60)
    print("🔧 Variables de Entorno")
    print("=" * 60)
    
    env_vars = {
        "CLOUD_API_URL": settings.CLOUD_API_URL,
        "CLOUD_API_ADMIN_TOKEN": settings.CLOUD_API_ADMIN_TOKEN[:10] + "..." if settings.CLOUD_API_ADMIN_TOKEN else None,
        "JWT_SECRET": "***" if settings.JWT_SECRET else None,
    }
    
    for var, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {value or 'NO CONFIGURADA'}")
    
    print("\n" + "=" * 60)
    
    # Verificar si hay errores 405
    has_405 = any(r == "METHOD_NOT_ALLOWED" for r in results.values())
    
    if has_405:
        print("\n⚠️  Se detectó error 405 (Method Not Allowed)")
        print("   Posibles causas:")
        print("   1. El Cloud API no tiene los endpoints /admin/* configurados")
        print("   2. Los endpoints existen pero están en una ruta diferente")
        print("   3. La URL apunta a un servicio diferente")
        print("\n   Solución:")
        print("   - Verifica que CLOUD_API_URL apunte al Cloud API correcto")
        print("   - Compara con el deployment que funciona:")
        print("     jevo-irrigation-production.up.railway.app")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = check_cloud_api_url()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
