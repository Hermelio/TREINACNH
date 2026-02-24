#!/usr/bin/env python
"""
Script para enviar email de boas-vindas à nova plataforma TreinaCNH.
Envia para:
  1. Alunos importados do CSV (StudentLead com accept_email=True)
  2. Instrutores/alunos já cadastrados como usuários Django
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import StudentLead
from django.core.mail import send_mail
from django.conf import settings
import time


SITE_URL = 'http://72.61.36.89:8080'
RESET_URL = f'{SITE_URL}/contas/senha/recuperar/'
REGISTER_URL = f'{SITE_URL}/contas/registrar/'


def build_html(name, is_lead=False, email=''):
    action_block = f"""
            <div class="highlight">
                <strong>⚠️ AÇÃO NECESSÁRIA:</strong> Finalize seu cadastro na nova plataforma para continuar acessando os recursos.
            </div>

            <h2>🔑 Como acessar a plataforma:</h2>
            <ol>
                <li>Clique no botão abaixo para criar sua conta</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Complete seu perfil e aproveite!</li>
            </ol>

            <center>
                <a href="{REGISTER_URL}" class="button">
                    🚀 Finalizar Meu Cadastro
                </a>
            </center>
""" if is_lead else f"""
            <div class="highlight">
                <strong>⚠️ AÇÃO NECESSÁRIA:</strong> Se ainda não acessou a nova plataforma, redefina sua senha para entrar.
            </div>

            <h2>🔑 Como acessar sua conta:</h2>
            <ol>
                <li>Clique no botão abaixo para redefinir sua senha</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Crie uma nova senha e faça login</li>
            </ol>

            <center>
                <a href="{RESET_URL}" class="button">
                    🔐 Recuperar Minha Senha
                </a>
            </center>
"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        h1 {{ margin: 0; font-size: 28px; }}
        h2 {{ color: #667eea; }}
        .highlight {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Bem-vindo à Nova TreinaCNH!</h1>
        </div>
        <div class="content">
            <p>Olá <strong>{name}</strong>,</p>

            <p>A plataforma <strong>TreinaCNH</strong> foi completamente renovada para oferecer a melhor experiência para conectar instrutores autônomos e alunos em todo o Brasil!</p>

            {action_block}

            <h2>📱 O que há de novo:</h2>
            <ul>
                <li>✅ Design moderno e responsivo</li>
                <li>✅ Sistema de busca de instrutores por cidade</li>
                <li>✅ Perfis completos com avaliações</li>
                <li>✅ Contato direto com instrutores verificados</li>
                <li>✅ Plataforma 100% gratuita para alunos</li>
            </ul>

            <p style="margin-top: 30px;">Se você tiver qualquer dúvida, estamos à disposição!</p>

            <p>Atenciosamente,<br><strong>Equipe TreinaCNH</strong></p>
        </div>
        <div class="footer">
            <p>© 2026 TreinaCNH - Conectando instrutores e alunos</p>
            <p>Este é um email automático, por favor não responda.</p>
        </div>
    </div>
</body>
</html>"""


def build_plain(name, is_lead=False, email=''):
    if is_lead:
        action = f"""⚠️ AÇÃO NECESSÁRIA: Finalize seu cadastro na nova plataforma!

🔑 Como acessar:
1. Acesse: {REGISTER_URL}
2. Use o email: {email}
3. Complete seu perfil e aproveite gratuitamente!"""
    else:
        action = f"""⚠️ AÇÃO NECESSÁRIA: Redefina sua senha para acessar a nova plataforma.

🔑 Como acessar:
1. Acesse: {RESET_URL}
2. Use o email: {email}
3. Crie uma nova senha e faça login."""

    return f"""Olá {name},

A plataforma TreinaCNH foi completamente renovada!

{action}

Se você tiver qualquer dúvida, estamos à disposição!

Atenciosamente,
Equipe TreinaCNH

---
© 2026 TreinaCNH - Este é um email automático, por favor não responda."""


def send_to_leads():
    """Envia para alunos importados do CSV (StudentLead) que ainda não são usuários."""
    # Emails que já têm conta Django para não enviar duplicado
    existing_emails = set(
        User.objects.filter(email__isnull=False).exclude(email='').values_list('email', flat=True)
    )

    leads = StudentLead.objects.filter(
        accept_email=True,
        email__isnull=False,
    ).exclude(email='')

    # Filtrar os que ainda não têm conta
    leads = [l for l in leads if l.email.lower() not in {e.lower() for e in existing_emails}]

    total = len(leads)
    print(f"\n👥 Alunos importados (CSV) sem conta: {total}")

    sent = 0
    errors = 0
    for lead in leads:
        try:
            send_mail(
                subject='🎉 Nova Plataforma TreinaCNH — Finalize seu Cadastro!',
                message=build_plain(lead.name.split()[0], is_lead=True, email=lead.email),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                html_message=build_html(lead.name.split()[0], is_lead=True, email=lead.email),
                fail_silently=False,
            )
            sent += 1
            print(f"  ✅ {sent}/{total} - {lead.email}")
            time.sleep(0.5)
        except Exception as e:
            errors += 1
            print(f"  ❌ Erro {lead.email}: {e}")

    return sent, errors, total


def send_to_users():
    """Envia para todos os usuários Django (instrutores e alunos cadastrados)."""
    users = User.objects.filter(
        is_active=True,
        email__isnull=False,
    ).exclude(email='').exclude(email__icontains='@example.com')

    total = users.count()
    print(f"\n👤 Usuários cadastrados na plataforma: {total}")

    sent = 0
    errors = 0
    for user in users:
        try:
            name = user.first_name or user.username
            send_mail(
                subject='🎉 Nova Plataforma TreinaCNH — Acesse Sua Conta!',
                message=build_plain(name, is_lead=False, email=user.email),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=build_html(name, is_lead=False, email=user.email),
                fail_silently=False,
            )
            sent += 1
            print(f"  ✅ {sent}/{total} - {user.email}")
            time.sleep(0.5)
        except Exception as e:
            errors += 1
            print(f"  ❌ Erro {user.email}: {e}")

    return sent, errors, total


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("   ENVIO DE EMAILS DE BOAS-VINDAS - TREINACNH")
    print("=" * 60)

    confirm = input("\n⚠️  Deseja enviar emails para TODOS (leads + usuários)? (sim/não): ")

    if confirm.lower() not in ['sim', 's', 'yes', 'y']:
        print("\n❌ Operação cancelada.")
        sys.exit(0)

    total_sent = 0
    total_errors = 0

    print("\n--- ETAPA 1: Alunos importados do CSV ---")
    s, e, t = send_to_leads()
    total_sent += s
    total_errors += e

    print("\n--- ETAPA 2: Usuários cadastrados na plataforma ---")
    s, e, t2 = send_to_users()
    total_sent += s
    total_errors += e

    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL:")
    print(f"   ✅ Emails enviados: {total_sent}")
    print(f"   ❌ Erros: {total_errors}")
    print("=" * 60)
    print("\n✅ Processo concluído!")


# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import time

def send_welcome_emails():
    """
    Envia emails de boas-vindas para todos os usuários cadastrados.
    """
    # Buscar usuários com email válido
    users = User.objects.filter(
        email__isnull=False,
        is_active=True
    ).exclude(email='').exclude(email__contains='@example.com')
    
    total = users.count()
    print(f"\n📧 Encontrados {total} usuários com email válido")
    print("=" * 60)
    
    sent_count = 0
    error_count = 0
    
    for user in users:
        try:
            # Identificar tipo de usuário
            user_type = "Instrutor" if hasattr(user, 'profile') and user.profile.is_instructor else "Aluno"
            
            # Dados do contexto
            context = {
                'user': user,
                'user_type': user_type,
                'site_url': 'https://treinacnh.com.br',
                'reset_url': 'https://treinacnh.com.br/accounts/password-reset/',
            }
            
            # Render HTML email
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
        h1 {{ margin: 0; font-size: 28px; }}
        h2 {{ color: #667eea; }}
        .highlight {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Bem-vindo à Nova TreinaCNH!</h1>
        </div>
        <div class="content">
            <p>Olá <strong>{user.first_name or user.username}</strong>,</p>
            
            <p>Estamos muito felizes em tê-lo(a) conosco! A plataforma <strong>TreinaCNH</strong> foi completamente renovada para oferecer a melhor experiência para conectar instrutores autônomos e alunos.</p>
            
            <div class="highlight">
                <strong>⚠️ AÇÃO NECESSÁRIA:</strong> Como migrado nossa plataforma, você precisa redefinir sua senha para acessar sua conta.
            </div>
            
            <h2>🔑 Como acessar sua conta:</h2>
            <ol>
                <li>Clique no botão abaixo para recuperar sua senha</li>
                <li>Digite seu email: <strong>{user.email}</strong></li>
                <li>Você receberá um link para criar uma nova senha</li>
                <li>Faça login e complete seu perfil</li>
            </ol>
            
            <center>
                <a href="https://treinacnh.com.br/accounts/password-reset/" class="button">
                    🔐 Recuperar Minha Senha
                </a>
            </center>
            
            <h2>📱 O que há de novo:</h2>
            <ul>
                <li>✅ Design moderno e responsivo</li>
                <li>✅ Sistema de busca aprimorado</li>
                <li>✅ Validação simplificada de instrutores</li>
                <li>✅ Melhor gestão de leads e contatos</li>
                <li>✅ Sistema de assinaturas integrado</li>
            </ul>
            
            <p style="margin-top: 30px;">Se você tiver qualquer dúvida, estamos à disposição!</p>
            
            <p>Atenciosamente,<br>
            <strong>Equipe TreinaCNH</strong></p>
        </div>
        <div class="footer">
            <p>© 2026 TreinaCNH - Conectando instrutores e alunos</p>
            <p>Este é um email automático, por favor não responda.</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Plain text version
            plain_message = f"""
Olá {user.first_name or user.username},

Estamos muito felizes em tê-lo(a) conosco! A plataforma TreinaCNH foi completamente renovada.

⚠️ AÇÃO NECESSÁRIA: 
Como migramos nossa plataforma, você precisa redefinir sua senha para acessar sua conta.

🔑 Como acessar sua conta:
1. Acesse: https://treinacnh.com.br/accounts/password-reset/
2. Digite seu email: {user.email}
3. Você receberá um link para criar uma nova senha
4. Faça login e complete seu perfil

Se você tiver qualquer dúvida, estamos à disposição!

Atenciosamente,
Equipe TreinaCNH

---
© 2026 TreinaCNH
Este é um email automático, por favor não responda.
"""
            
            # Enviar email
            send_mail(
                subject='🎉 Bem-vindo à Nova Plataforma TreinaCNH - Acesse Sua Conta',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            sent_count += 1
            print(f"✅ {sent_count}/{total} - Enviado para: {user.email} ({user_type})")
            
            # Pausa para não sobrecarregar o servidor SMTP
            time.sleep(0.5)
            
        except Exception as e:
            error_count += 1
            print(f"❌ Erro ao enviar para {user.email}: {e}")
            continue
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMO:")
    print(f"   Total de usuários: {total}")
    print(f"   ✅ Emails enviados: {sent_count}")
    print(f"   ❌ Erros: {error_count}")
    print("=" * 60)

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("   ENVIO DE EMAILS DE BOAS-VINDAS - TREINACNH")
    print("=" * 60)
    
    confirm = input("\n⚠️  Deseja enviar emails para TODOS os usuários cadastrados? (sim/não): ")
    
    if confirm.lower() in ['sim', 's', 'yes', 'y']:
        send_welcome_emails()
        print("\n✅ Processo concluído!")
    else:
        print("\n❌ Operação cancelada.")
