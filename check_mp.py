import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()
from django.conf import settings
import mercadopago

print("=" * 60)
print("DIAGNOSTICO MERCADO PAGO - TREINACNH")
print("=" * 60)

print("\n1. CONFIGURACOES:")
t = settings.MERCADOPAGO_ACCESS_TOKEN
pk = settings.MERCADOPAGO_PUBLIC_KEY
print(f"   ACCESS_TOKEN: {'OK (' + str(len(t)) + ' chars)' if t else 'NAO CONFIGURADO!'}")
print(f"   PUBLIC_KEY:   {'OK' if pk else 'NAO CONFIGURADO!'}")
print(f"   COLLECTOR_ID: {getattr(settings, 'MERCADOPAGO_COLLECTOR_ID', 'N/A')}")
print(f"   SITE_URL:     {settings.SITE_URL}")
print(f"   DEBUG:        {settings.DEBUG}")

# Planos
from billing.models import Plan, Subscription, Payment
print("\n2. PLANOS ATIVOS:")
plans = Plan.objects.filter(is_active=True)
for p in plans:
    print(f"   - {p.name}: R$ {p.price_monthly}/mes")
if not plans:
    print("   NENHUM PLANO ATIVO!")

# Assinaturas + pagamentos
print("\n3. ASSINATURAS (ultimas 5):")
for s in Subscription.objects.select_related('instructor__user', 'plan').order_by('-created_at')[:5]:
    print(f"   - {s.instructor.user.username} | {s.plan.name} | {s.status} | ate {s.end_date}")

print("\n4. PAGAMENTOS (ultimos 5):")
pymnts = Payment.objects.order_by('-created_at')[:5]
if pymnts:
    for p in pymnts:
        print(f"   - {p.external_id[:40]} | {p.status} | R${p.amount}")
else:
    print("   Nenhum pagamento registrado.")

# Teste MP
print("\n5. TESTE DE PREFERENCIA MP:")
try:
    sdk = mercadopago.SDK(t)
    plan = Plan.objects.filter(is_active=True).first()
    if plan:
        resp = sdk.preference().create({
            "items": [{"title": f"{plan.name} - TreinaCNH", "quantity": 1, "unit_price": float(plan.price_monthly), "currency_id": "BRL"}],
            "back_urls": {
                "success": f"{settings.SITE_URL}/planos/pagamento/sucesso/",
                "failure": f"{settings.SITE_URL}/planos/pagamento/falha/",
                "pending": f"{settings.SITE_URL}/planos/pagamento/pendente/",
            },
            "notification_url": f"{settings.SITE_URL}/webhook/mercadopago/",
            "external_reference": "test_diagnostico",
        })
        if resp.get("status") == 201:
            pref = resp["response"]
            print(f"   STATUS: OK!")
            print(f"   INIT_POINT: {pref['init_point']}")
            print(f"   SANDBOX: {pref.get('sandbox_init_point', 'N/A')}")
        else:
            print(f"   ERRO: {resp.get('status')} - {resp.get('response')}")
except Exception as e:
    print(f"   EXCECAO: {e}")

print("\n" + "=" * 60)
