#!/usr/bin/env python3
"""
Contract verification script for Cloud API (Railway deployment)
Validates that Cloud API responses match Admin UI template expectations.

Usage:
    cd backend
    python scripts/contract_check.py
"""
import os
import sys
import httpx
from typing import Optional, Dict, Any

# Load env from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

CLOUD_API_URL = os.getenv("CLOUD_API_URL")
CLOUD_API_ADMIN_TOKEN = os.getenv("CLOUD_API_ADMIN_TOKEN")

if not CLOUD_API_URL or not CLOUD_API_ADMIN_TOKEN:
    print("❌ Missing required environment variables:")
    print("   CLOUD_API_URL:", CLOUD_API_URL)
    print("   CLOUD_API_ADMIN_TOKEN:", "***" if CLOUD_API_ADMIN_TOKEN else None)
    sys.exit(1)

print(f"🔗 Cloud API URL: {CLOUD_API_URL}")
print(f"🔑 Admin Token: {'***' + CLOUD_API_ADMIN_TOKEN[-4:] if len(CLOUD_API_ADMIN_TOKEN) > 4 else '***'}")
print()

def make_request(method: str, path: str) -> Optional[Dict[str, Any]]:
    """Make authenticated request to Cloud API"""
    url = f"{CLOUD_API_URL}{path}"
    headers = {"Authorization": f"Bearer {CLOUD_API_ADMIN_TOKEN}"}
    
    try:
        response = httpx.request(method, url, headers=headers, timeout=10.0)
        print(f"  {method} {path} -> {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"    ⚠️  404 Not Found")
            return None
        else:
            print(f"    ❌ Error: {response.text[:100]}")
            return None
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        return None

def check_clients():
    """Verify /admin/clients endpoint"""
    print("📋 Checking Clients...")
    data = make_request("GET", "/admin/clients")
    
    if not data:
        print("  ⚠️  No clients data returned")
        return None
    
    if not isinstance(data, list):
        print(f"  ❌ Expected list, got {type(data)}")
        return None
    
    print(f"  ✅ Got {len(data)} clients")
    
    if len(data) > 0:
        first = data[0]
        print(f"  📦 First client: {first.get('code', 'N/A')}")
        
        # Check required fields for list view
        required = ["code", "name"]
        missing = [f for f in required if f not in first]
        if missing:
            print(f"    ⚠️  Missing fields: {missing}")
        
        return first.get("code")
    
    return None

def check_client_detail(code: str):
    """Verify /admin/clients/{code} endpoint"""
    print(f"\n📄 Checking Client Detail: {code}...")
    data = make_request("GET", f"/admin/clients/{code}")
    
    if not data:
        print("  ⚠️  No client detail returned")
        return
    
    # Check fields required by edit_client.html template
    # Template expects: client.code, client.name, terminology.unit_terms, etc.
    required_client = ["code", "name"]
    optional_client = ["contact_email", "whatsapp_number", "terminology"]
    
    missing = [f for f in required_client if f not in data]
    if missing:
        print(f"  ❌ Missing required fields: {missing}")
    else:
        print(f"  ✅ Has required client fields")
    
    # Check terminology structure (required by template at root context)
    if "terminology" in data:
        term = data["terminology"]
        term_fields = ["unit_terms", "group_terms", "program_terms"]
        term_missing = [f for f in term_fields if f not in term]
        if term_missing:
            print(f"  ⚠️  Terminology missing: {term_missing}")
        else:
            print(f"  ✅ Terminology structure OK")
    else:
        print(f"  ⚠️  No terminology field (template needs it)")

def check_fields():
    """Verify /admin/fields endpoint"""
    print("\n📋 Checking Fields...")
    data = make_request("GET", "/admin/fields")
    
    if not data:
        print("  ⚠️  No fields data returned")
        return None, None
    
    # Response might be dict with {fields: [...], clients: [...]}
    fields_list = data.get("fields", []) if isinstance(data, dict) else data
    
    if not isinstance(fields_list, list):
        print(f"  ❌ Expected fields list, got {type(fields_list)}")
        return None, None
    
    print(f"  ✅ Got {len(fields_list)} fields")
    
    if len(fields_list) > 0:
        first = fields_list[0]
        client_code = first.get("client_code") or first.get("client", {}).get("code")
        field_code = first.get("field_code") or first.get("code")
        
        print(f"  📦 First field: {client_code}/{field_code}")
        
        # Check required fields for list view
        required = ["name"]
        missing = [f for f in required if f not in first]
        if missing:
            print(f"    ⚠️  Missing fields: {missing}")
        
        return client_code, field_code
    
    return None, None

def check_field_detail(client_code: str, field_code: str):
    """Verify /admin/fields/{client}/{field} endpoint"""
    print(f"\n📄 Checking Field Detail: {client_code}/{field_code}...")
    data = make_request("GET", f"/admin/fields/{client_code}/{field_code}")
    
    if not data:
        print("  ⚠️  No field detail returned")
        return
    
    # Check fields required by edit_field.html template
    # Template expects: field.client.code, field.client.name, field.code, field.name
    # Also: icc_credentials.{host,port,dbname,user}, nomenclature.{aliases,units_text,groups_text}
    
    required = ["code", "name"]
    missing = [f for f in required if f not in data]
    if missing:
        print(f"  ❌ Missing required fields: {missing}")
    else:
        print(f"  ✅ Has required field fields")
    
    # Check client structure
    if "client" in data and isinstance(data["client"], dict):
        client_fields = ["code", "name"]
        client_missing = [f for f in client_fields if f not in data["client"]]
        if client_missing:
            print(f"  ⚠️  field.client missing: {client_missing}")
        else:
            print(f"  ✅ field.client structure OK")
    else:
        print(f"  ⚠️  No nested client object (template needs field.client.code)")
    
    # Check icc_credentials
    if "icc_credentials" in data:
        icc = data["icc_credentials"]
        icc_fields = ["host", "port", "dbname", "user"]
        icc_missing = [f for f in icc_fields if f not in icc]
        if icc_missing:
            print(f"  ⚠️  icc_credentials missing: {icc_missing}")
        else:
            print(f"  ✅ icc_credentials structure OK")
    else:
        print(f"  ⚠️  No icc_credentials (template expects it)")
    
    # Check nomenclature
    if "nomenclature" in data:
        nom = data["nomenclature"]
        nom_fields = ["aliases", "units_text", "groups_text"]
        nom_missing = [f for f in nom_fields if f not in nom]
        if nom_missing:
            print(f"  ⚠️  nomenclature missing: {nom_missing}")
        else:
            print(f"  ✅ nomenclature structure OK")
    else:
        print(f"  ⚠️  No nomenclature (template expects it)")

def check_whatsapp_users():
    """Verify /admin/whatsapp-users endpoint"""
    print("\n📋 Checking WhatsApp Users...")
    data = make_request("GET", "/admin/whatsapp-users")
    
    if not data:
        print("  ⚠️  No whatsapp users data returned")
        return None
    
    # Response might be dict with {users: [...], fields: [...]}
    users_list = data.get("users", []) if isinstance(data, dict) else data
    
    if not isinstance(users_list, list):
        print(f"  ❌ Expected users list, got {type(users_list)}")
        return None
    
    print(f"  ✅ Got {len(users_list)} WhatsApp users")
    
    if len(users_list) > 0:
        first = users_list[0]
        user_id = first.get("id")
        
        print(f"  📦 First user: {first.get('phone_number', 'N/A')} (ID: {user_id})")
        
        # Check required fields for list view
        required = ["id", "phone_number"]
        missing = [f for f in required if f not in first]
        if missing:
            print(f"    ⚠️  Missing fields: {missing}")
        
        return user_id
    
    return None

def check_whatsapp_user_detail(user_id: str):
    """Verify /admin/whatsapp-users/{id} endpoint"""
    print(f"\n📄 Checking WhatsApp User Detail: {user_id}...")
    data = make_request("GET", f"/admin/whatsapp-users/{user_id}")
    
    if not data:
        print("  ⚠️  No user detail returned")
        return
    
    # Check fields required by edit_whatsapp_user.html template
    # Template expects: user.id, user.phone_number, user.display_name, user.is_active
    # Also needs fields list for checkboxes (fetched separately in router)
    
    required = ["id", "phone_number"]
    optional = ["display_name", "is_active", "field_ids"]
    
    missing = [f for f in required if f not in data]
    if missing:
        print(f"  ❌ Missing required fields: {missing}")
    else:
        print(f"  ✅ Has required user fields")
    
    present_optional = [f for f in optional if f in data]
    if present_optional:
        print(f"  ℹ️  Optional fields present: {present_optional}")

def main():
    print("=" * 60)
    print("Cloud API Contract Verification")
    print("=" * 60)
    print()
    
    # Check clients
    client_code = check_clients()
    if client_code:
        check_client_detail(client_code)
    
    # Check fields
    client_code, field_code = check_fields()
    if client_code and field_code:
        check_field_detail(client_code, field_code)
    
    # Check WhatsApp users
    user_id = check_whatsapp_users()
    if user_id:
        check_whatsapp_user_detail(user_id)
    
    print("\n" + "=" * 60)
    print("✅ Contract verification complete")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review any ⚠️  warnings above")
    print("2. If response shapes don't match templates, update router context building")
    print("3. DO NOT modify templates unless absolutely necessary")

if __name__ == "__main__":
    main()
