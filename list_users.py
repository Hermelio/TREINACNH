from django.contrib.auth.models import User
from billing.models import Subscription

users = User.objects.filter(profile__role='INSTRUCTOR')
print(f'\n📊 Total de instrutores: {users.count()}\n')

for u in users[:5]:
    print(f'Email: {u.email}, Nome: {u.get_full_name()}')
    subs = Subscription.objects.filter(user=u)
    if subs.exists():
        for s in subs:
            print(f'  └─ Assinatura: {s.plan.name}, Ativa: {s.is_active}, Fim: {s.end_date}')
    print()

print('\n---\nQual o email do usuário para remover a assinatura?')
