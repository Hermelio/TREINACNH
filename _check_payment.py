import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from billing.models import Subscription, Payment

print("\n=== SUBSCRIPTION_4 ===")
s = Subscription.objects.filter(id=4).select_related('plan','instructor__user').first()
if s:
    print(f"Plano: {s.plan.name}")
    print(f"Status: {s.status}")
    print(f"is_active: {s.is_active}")
    print(f"Inicio: {s.start_date}")
    print(f"Fim: {s.end_date}")
    print(f"Instrutor: {s.instructor.user.username}")
else:
    print("NAO ENCONTRADA")

print("\n=== PAYMENT 1344882061 ===")
p = Payment.objects.filter(external_id='1344882061').first()
if p:
    print(f"Status: {p.status}")
    print(f"Valor: R$ {p.amount}")
    print(f"Metodo: {p.payment_method}")
    print(f"Pago em: {p.paid_at}")
else:
    print("NAO ENCONTRADO - webhook pode nao ter chegado")
    print("\nTodos os payments existentes:")
    for pp in Payment.objects.all():
        print(f"  ID={pp.id} external_id={pp.external_id} status={pp.status}")
