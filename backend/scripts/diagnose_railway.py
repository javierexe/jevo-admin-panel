#!/usr/bin/env python3
"""
Script de diagnóstico para ejecutar EN RAILWAY.
Verifica la configuración y conectividad desde el mismo ambiente de producción.
"""

import os
import sys
import httpx
import json


def diagnose_railway_env():
    """Diagnóstico de variables de entorno en Railway."""
    
    print("=" * 70)
    print("🔧 RAILWAY ENVIRONMENT DIAGNOSIS")
    print("=" * 70)
    
    # Variables críticas
    env_vars = {
        "CLOUD_API_URL": os.getenv("CLOUD_API_URL"),
        "CLOUD_API_ADMIN_TOKEN": os.getenv("CLOUD_API_ADMIN_TOKEN"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME"),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "JWT_SECRET": os.getenv("JWT_SECRET"),
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT"),
        "RAILWAY_SERVICE_NAME": os.getenv("RAILWAY_SERVICE_NAME"),
    }
    
    print("\n📋 Environment Variables:")
    for key, value in env_vars.items():
        if value is None:
            print(f"  ❌ {key}: NOT SET")
        elif key in ["CLOUD_API_ADMIN_TOKEN", "ADMIN_PASSWORD", "JWT_SECRET", "DATABASE_URL"]:
            print(f"  ✅ {key}: {value[:15]}...")
        else:
            print(f"  ✅ {key}: {value}")
    
    return env_vars


def test_cloud_api_from_railway():
    """Prueba la conexión al Cloud API desde Railway."""
    
    cloud_api_url = os.getenv("CLOUD_API_URL")
    admin_token = os.getenv("CLOUD_API_ADMIN_TOKEN")
    
    if not cloud_api_url or not admin_token:
        print("\n❌ ERROR: CLOUD_API_URL o CLOUD_API_ADMIN_TOKEN no están configurados")
        return False
    
    print("\n" + "=" * 70)
    print("🧪 TESTING CLOUD API FROM RAILWAY")
    print("=" * 70)
    
    endpoints = [
        "/health",
        "/admin/clients",
        "/admin/fields",
        "/admin/whatsapp-users"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        full_url = f"{cloud_api_url}{endpoint}"
        print(f"\n🎯 GET {full_url}")
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    full_url,
                    headers={
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    },
                    follow_redirects=True
                )
                
                status = response.status_code
                print(f"   Status: {status}")
                
                if status == 200:
                    print(f"   ✅ SUCCESS")
                    try:
                        data = response.json()
                        print(f"   Data type: {type(data)}")
                        if isinstance(data, list):
                            print(f"   Items count: {len(data)}")
                        elif isinstance(data, dict):
                            print(f"   Keys: {list(data.keys())}")
                    except:
                        print(f"   Body: {response.text[:100]}")
                elif status == 401:
                    print(f"   ❌ UNAUTHORIZED")
                    print(f"   Detail: {response.text[:200]}")
                elif status == 404:
                    print(f"   ❌ NOT FOUND")
                elif status == 405:
                    print(f"   ❌ METHOD NOT ALLOWED ⚠️")
                    print(f"   Detail: {response.text[:200]}")
                    print(f"   Headers: {dict(response.headers)}")
                else:
                    print(f"   ⚠️  Status {status}")
                    print(f"   Body: {response.text[:200]}")
                
                results[endpoint] = status
                
        except httpx.ConnectError as e:
            print(f"   ❌ CONNECTION ERROR: {e}")
            results[endpoint] = "CONN_ERROR"
        except httpx.TimeoutException:
            print(f"   ❌ TIMEOUT")
            results[endpoint] = "TIMEOUT"
        except Exception as e:
            print(f"   ❌ ERROR: {type(e).__name__}: {e}")
            results[endpoint] = "ERROR"
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    for endpoint, status in results.items():
        if status == 200:
            emoji = "✅"
        elif status == 405:
            emoji = "⚠️"
        else:
            emoji = "❌"
        print(f"  {emoji} {endpoint}: {status}")
    
    has_405 = any(s == 405 for s in results.values())
    
    if has_405:
        print("\n" + "=" * 70)
        print("⚠️  DETECTED 405 ERRORS")
        print("=" * 70)
        print("\nPossible causes:")
        print("1. CLOUD_API_URL points to wrong service")
        print("2. Cloud API doesn't have /admin/* routes")
        print("3. Middleware/proxy blocking the method")
        print("\nVerify:")
        print(f"  - CLOUD_API_URL should be: https://jevo-irrigation-production.up.railway.app")
        print(f"  - Current value: {cloud_api_url}")
    
    return not has_405


if __name__ == "__main__":
    print("\n🚂 Running from Railway environment\n")
    
    # Diagnose environment
    env_vars = diagnose_railway_env()
    
    # Test Cloud API
    success = test_cloud_api_from_railway()
    
    print("\n" + "=" * 70)
    print("✨ DIAGNOSIS COMPLETE")
    print("=" * 70 + "\n")
    
    sys.exit(0 if success else 1)
