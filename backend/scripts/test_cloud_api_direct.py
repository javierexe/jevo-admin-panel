#!/usr/bin/env python3
"""
Script para probar directamente la conexión con el Cloud API.
Útil para debugging de problemas de autenticación o conectividad.
"""

import os
import sys
import httpx
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def test_cloud_api_connection():
    """Prueba la conexión directa al Cloud API con el token configurado."""
    
    print("=" * 70)
    print("🧪 TEST DIRECTO: Cloud API Connection")
    print("=" * 70)
    
    cloud_api_url = settings.CLOUD_API_URL
    admin_token = settings.CLOUD_API_ADMIN_TOKEN
    
    print(f"\n📍 CLOUD_API_URL: {cloud_api_url}")
    print(f"🔑 CLOUD_API_ADMIN_TOKEN: {admin_token[:20]}...{admin_token[-10:] if len(admin_token) > 30 else admin_token}")
    
    # Test endpoint
    endpoint = "/admin/clients"
    full_url = f"{cloud_api_url}{endpoint}"
    
    print(f"\n🎯 Testing: GET {full_url}")
    print(f"   Headers:")
    print(f"     Authorization: Bearer {admin_token[:10]}...")
    print(f"     Content-Type: application/json")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                full_url,
                headers={
                    "Authorization": f"Bearer {admin_token}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"\n📊 RESPONSE:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                try:
                    data = response.json()
                    print(f"   Data: {data[:200] if len(str(data)) > 200 else data}")
                except:
                    print(f"   Body: {response.text[:200]}")
            elif response.status_code == 401:
                print(f"   ❌ UNAUTHORIZED")
                print(f"   Detail: {response.text}")
                print(f"\n   💡 El token admin es incorrecto o no está configurado en el Cloud API")
                print(f"   Verifica que ADMIN_TOKEN en jevo-irrigation-production sea el mismo")
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND")
                print(f"   Detail: {response.text}")
                print(f"\n   💡 El endpoint {endpoint} no existe en {cloud_api_url}")
            elif response.status_code == 405:
                print(f"   ❌ METHOD NOT ALLOWED")
                print(f"   Detail: {response.text}")
                print(f"\n   💡 ESTE ES EL ERROR QUE ESTÁS VIENDO EN PRODUCCIÓN")
                print(f"   Causas posibles:")
                print(f"   1. El Cloud API no acepta GET en {endpoint}")
                print(f"   2. Hay un proxy/gateway intermedio rechazando el request")
                print(f"   3. CORS o middleware bloqueando el método")
            else:
                print(f"   ⚠️  UNEXPECTED STATUS: {response.status_code}")
                print(f"   Body: {response.text[:500]}")
            
            return response.status_code
            
    except httpx.ConnectError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print(f"   No se puede conectar a {cloud_api_url}")
        print(f"   Verifica que el URL sea correcto y el servicio esté corriendo")
        return None
    except httpx.TimeoutException:
        print(f"\n❌ TIMEOUT: Request tardó más de 10 segundos")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_multiple_endpoints():
    """Prueba varios endpoints para ver cuáles funcionan."""
    
    endpoints = [
        ("/admin/clients", "GET"),
        ("/admin/fields", "GET"),
        ("/admin/whatsapp-users", "GET"),
        ("/health", "GET"),
        ("/", "GET"),
    ]
    
    print("\n" + "=" * 70)
    print("🔍 TESTING MULTIPLE ENDPOINTS")
    print("=" * 70)
    
    results = {}
    
    for endpoint, method in endpoints:
        full_url = f"{settings.CLOUD_API_URL}{endpoint}"
        print(f"\n  {method} {full_url}...", end=" ")
        
        try:
            with httpx.Client(timeout=5.0) as client:
                if method == "GET":
                    response = client.get(
                        full_url,
                        headers={
                            "Authorization": f"Bearer {settings.CLOUD_API_ADMIN_TOKEN}",
                            "Content-Type": "application/json"
                        }
                    )
                
                status = response.status_code
                
                if status == 200:
                    print(f"✅ {status}")
                elif status == 401:
                    print(f"🔐 {status} (auth)")
                elif status == 404:
                    print(f"❌ {status} (not found)")
                elif status == 405:
                    print(f"⚠️  {status} (METHOD NOT ALLOWED) ⚠️")
                else:
                    print(f"⚠️  {status}")
                
                results[endpoint] = status
                
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}")
            results[endpoint] = "ERROR"
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for endpoint, status in results.items():
        emoji = "✅" if status == 200 else "🔐" if status == 401 else "❌"
        print(f"  {emoji} {endpoint}: {status}")
    
    return results


if __name__ == "__main__":
    print("\n")
    
    # Test 1: Direct connection
    status_code = test_cloud_api_connection()
    
    # Test 2: Multiple endpoints
    print("\n")
    results = test_multiple_endpoints()
    
    print("\n" + "=" * 70)
    print("✨ TEST COMPLETED")
    print("=" * 70 + "\n")
    
    sys.exit(0 if status_code == 200 else 1)
