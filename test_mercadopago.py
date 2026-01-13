#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("Verificando configurações do Mercado Pago:")
print("=" * 60)

if hasattr(settings, 'MERCADOPAGO_ACCESS_TOKEN'):
    token = settings.MERCADOPAGO_ACCESS_TOKEN
    print(f"✅ ACCESS_TOKEN configurado: {token[:20]}...{token[-10:]}")
else:
    print("❌ ACCESS_TOKEN NÃO configurado")

if hasattr(settings, 'MERCADOPAGO_PUBLIC_KEY'):
    key = settings.MERCADOPAGO_PUBLIC_KEY
    print(f"✅ PUBLIC_KEY configurado: {key[:20]}...{key[-10:]}")
else:
    print("❌ PUBLIC_KEY NÃO configurado")

if hasattr(settings, 'SITE_URL'):
    print(f"✅ SITE_URL: {settings.SITE_URL}")
else:
    print("❌ SITE_URL NÃO configurado")

print("=" * 60)

# Test Mercado Pago SDK
try:
    import mercadopago
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    print("✅ SDK Mercado Pago inicializado com sucesso")
    
    # Try to create a simple preference
    test_preference = {
        "items": [
            {
                "title": "Test",
                "quantity": 1,
                "unit_price": 10.0,
                "currency_id": "BRL",
            }
        ]
    }
    response = sdk.preference().create(test_preference)
    if response["status"] == 201:
        print("✅ Teste de criação de preference: OK")
    else:
        print(f"❌ Erro ao criar preference de teste: {response}")
except Exception as e:
    print(f"❌ Erro ao testar SDK: {str(e)}")
