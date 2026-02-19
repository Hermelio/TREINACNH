#!/usr/bin/env python
"""Remove assinatura e pagamentos do admin para novo teste"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from billing.models import Subscription, Payment
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ASSINATURAS EXISTENTES")
print("="*60)

subs = Subscription.objects.select_related('instructor__user', 'plan').all()
if not subs.exists():
    print("Nenhuma assinatura encontrada.")
else:
    for s in subs:
        payments = s.payments.count()
        print(f"ID={s.id} | user={s.instructor.user.username} | email={s.instructor.user.email} | plano={s.plan.name} | status={s.status} | pagamentos={payments}")

print("\n" + "="*60)
print("REMOVENDO ASSINATURAS DO ADMIN")
print("="*60)

# Remove assinaturas de usuários admin/superuser
admin_subs = Subscription.objects.filter(instructor__user__is_superuser=True)
if not admin_subs.exists():
    # Tenta pelo username contendo 'admin'
    admin_subs = Subscription.objects.filter(instructor__user__username__icontains='admin')

count = admin_subs.count()
if count == 0:
    print("Nenhuma assinatura de admin encontrada.")
    print("Listando todos os usuários com assinatura para escolher manualmente:")
    for s in Subscription.objects.select_related('instructor__user'):
        print(f"  -> username: {s.instructor.user.username}")
else:
    # Remove pagamentos vinculados
    for s in admin_subs:
        pcount = s.payments.count()
        s.payments.all().delete()
        print(f"Removidos {pcount} pagamento(s) da assinatura ID={s.id}")
    admin_subs.delete()
    print(f"\n✅ {count} assinatura(s) de admin removida(s) com sucesso!")
    print("✅ Pode testar o fluxo de compra do zero agora.")
