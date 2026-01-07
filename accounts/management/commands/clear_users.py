"""
Management command to clear all users from database.
Usage: python manage.py clear_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Remove all users from database'

    def handle(self, *args, **kwargs):
        user_count = User.objects.count()
        
        if user_count == 0:
            self.stdout.write(self.style.WARNING('Nenhum usuário encontrado no banco.'))
            return
        
        self.stdout.write(self.style.WARNING(f'Você está prestes a deletar {user_count} usuários.'))
        confirm = input('Tem certeza? Digite "sim" para confirmar: ')
        
        if confirm.lower() == 'sim':
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'✓ {user_count} usuários deletados com sucesso!'))
            self.stdout.write(self.style.SUCCESS('Banco limpo. Você pode criar novos usuários agora.'))
        else:
            self.stdout.write(self.style.ERROR('Operação cancelada.'))
