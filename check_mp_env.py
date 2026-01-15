#!/usr/bin/env python
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

access_token = settings.MERCADOPAGO_ACCESS_TOKEN

# Check if token is test or production
print("Verificando ambiente do Mercado Pago...")
print("=" * 60)
print(f"Access Token: {access_token[:30]}...")

# Make a test API call
url = "https://api.mercadopago.com/v1/payment_methods"
headers = {"Authorization": f"Bearer {access_token}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Token válido!")
    
    # Check if it's test or production by the token format
    if access_token.startswith("TEST-"):
        print("🟢 Ambiente: TESTE")
    elif access_token.startswith("APP_USR-"):
        print("🔴 Ambiente: PRODUÇÃO")
    else:
        print("❓ Ambiente: DESCONHECIDO")
        
    print("\nPara verificar, vamos criar uma preference de teste...")
    
    import mercadopago
    sdk = mercadopago.SDK(access_token)
    
    test_pref = {
        "items": [{
            "title": "Test",
            "quantity": 1,
            "unit_price": 10.0
        }]
    }
    
    result = sdk.preference().create(test_pref)
    if result["status"] == 201:
        pref = result["response"]
        print(f"✅ Preference criada: {pref['id']}")
        print(f"Init Point: {pref['init_point']}")
        
        # Check the init_point URL - sandbox means test
        if 'sandbox' in pref['init_point']:
            print("\n🟢 CONFIRMADO: Credenciais de TESTE (usa sandbox)")
        else:
            print("\n🔴 CONFIRMADO: Credenciais de PRODUÇÃO (não usa sandbox)")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
