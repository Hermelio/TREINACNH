#!/usr/bin/env python
"""
Executa o envio de emails diretamente sem confirmacao interativa.
Usa uma unica conexao SMTP reutilizada para todos os emails (evita rate limit do Gmail).
"""
import os, sys, django, time
sys.path.insert(0, '/var/www/TREINACNH')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from marketplace.models import StudentLead
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings

SITE_URL = 'http://72.61.36.89:8080'
RESET_URL = f'{SITE_URL}/contas/senha/recuperar/'
REGISTER_URL = f'{SITE_URL}/contas/registrar/'

DELAY = 3  # segundos entre emails — evita rate limit do Gmail

# Emails ja enviados com sucesso no run anterior (nao reenviar)
ALREADY_SENT = {
    'marivone.silva@hotmail.com',
    'caianahiago02@gmail.com',
    'espacolinikher@gmail.com',
    'medeirosoverral@gmail.com',
    'kaduriber15@gmail.com',
    'eloiza.lima0518@gmail.com',
    'nicolassiqueira51@gmail.com',
    'amarolaylson@gmail.com',
    'santosjardel179@gmail.com',
}


def build_html(name, is_lead=False, email=''):
    action_block = f"""
            <div class="highlight">
                <strong>&#9888; AÇÃO NECESSÁRIA:</strong> Finalize seu cadastro na nova plataforma para continuar acessando os recursos.
            </div>
            <h2>&#128273; Como acessar a plataforma:</h2>
            <ol>
                <li>Clique no botão abaixo para criar sua conta</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Complete seu perfil e aproveite!</li>
            </ol>
            <center><a href="{REGISTER_URL}" class="button">Finalizar Meu Cadastro</a></center>
""" if is_lead else f"""
            <div class="highlight">
                <strong>&#9888; AÇÃO NECESSÁRIA:</strong> Se ainda não acessou a nova plataforma, redefina sua senha para entrar.
            </div>
            <h2>&#128273; Como acessar sua conta:</h2>
            <ol>
                <li>Clique no botão abaixo para redefinir sua senha</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Crie uma nova senha e faça login</li>
            </ol>
            <center><a href="{RESET_URL}" class="button">Recuperar Minha Senha</a></center>
"""
    return f"""<!DOCTYPE html><html><head><style>
        body{{font-family:Arial,sans-serif;line-height:1.6;color:#333}}
        .container{{max-width:600px;margin:0 auto;padding:20px}}
        .header{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:30px;text-align:center;border-radius:10px 10px 0 0}}
        .content{{background:#f9f9f9;padding:30px;border-radius:0 0 10px 10px}}
        .button{{display:inline-block;padding:15px 30px;background:#667eea;color:white;text-decoration:none;border-radius:5px;margin:20px 0}}
        .footer{{text-align:center;margin-top:30px;color:#999;font-size:12px}}
        h1{{margin:0;font-size:28px}} h2{{color:#667eea}}
        .highlight{{background:#fff3cd;padding:15px;border-left:4px solid #ffc107;margin:20px 0}}
    </style></head><body><div class="container">
        <div class="header"><h1>Bem-vindo a Nova TreinaCNH!</h1></div>
        <div class="content">
            <p>Ola <strong>{name}</strong>,</p>
            <p>A plataforma <strong>TreinaCNH</strong> foi completamente renovada para conectar instrutores autonomos e alunos em todo o Brasil!</p>
            {action_block}
            <h2>O que ha de novo:</h2>
            <ul>
                <li>Design moderno e responsivo</li>
                <li>Sistema de busca de instrutores por cidade</li>
                <li>Perfis completos com avaliacoes</li>
                <li>Contato direto com instrutores verificados</li>
                <li>Plataforma 100% gratuita para alunos</li>
            </ul>
            <p>Atenciosamente,<br><strong>Equipe TreinaCNH</strong></p>
        </div>
        <div class="footer">
            <p>2026 TreinaCNH - Conectando instrutores e alunos</p>
            <p>Este e um email automatico, por favor nao responda.</p>
        </div>
    </div></body></html>"""


def build_plain(name, is_lead=False, email=''):
    if is_lead:
        return f"Ola {name},\n\nA plataforma TreinaCNH foi renovada!\n\nFinalize seu cadastro em: {REGISTER_URL}\nUse o email: {email}\n\nEquipe TreinaCNH"
    return f"Ola {name},\n\nA plataforma TreinaCNH foi renovada!\n\nRecupere sua senha em: {RESET_URL}\nUse o email: {email}\n\nEquipe TreinaCNH"


def send_batch(items, is_lead, label):
    """Envia uma lista de (name, email) reutilizando a conexao SMTP."""
    sent = errors = 0
    total = len(items)
    print(f"\n--- {label}: {total} destinatarios ---", flush=True)

    connection = get_connection()
    connection.open()
    print("  Conexao SMTP aberta.", flush=True)

    for i, (name, email) in enumerate(items, 1):
        if email.lower() in ALREADY_SENT:
            print(f"  SKIP {i}/{total} {email} (ja enviado)", flush=True)
            continue
        try:
            subject = ('Nova Plataforma TreinaCNH - Finalize seu Cadastro!'
                       if is_lead else
                       'Nova Plataforma TreinaCNH - Acesse Sua Conta!')
            msg = EmailMultiAlternatives(
                subject=subject,
                body=build_plain(name, is_lead=is_lead, email=email),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection,
            )
            msg.attach_alternative(build_html(name, is_lead=is_lead, email=email), 'text/html')
            msg.send()
            sent += 1
            ALREADY_SENT.add(email.lower())
            print(f"  OK {i}/{total} {email}", flush=True)
            time.sleep(DELAY)
        except Exception as e:
            errors += 1
            print(f"  ERRO {email}: {e}", flush=True)
            # Reabrir conexao se caiu
            try:
                connection.close()
                time.sleep(10)
                connection.open()
                print("  Conexao SMTP reaberta.", flush=True)
            except Exception as e2:
                print(f"  Falha ao reabrir conexao: {e2}", flush=True)

    try:
        connection.close()
    except Exception:
        pass
    return sent, errors


# ---- LEADS DO CSV ----
existing_emails = set(User.objects.exclude(email='').values_list('email', flat=True))
leads_qs = [l for l in StudentLead.objects.filter(accept_email=True).exclude(email='')
            if l.email.lower() not in {e.lower() for e in existing_emails}]
leads_items = [(l.name.split()[0] if l.name else 'Aluno', l.email) for l in leads_qs]

sent_l, errors_l = send_batch(leads_items, is_lead=True, label='ETAPA 1: alunos importados do CSV')

# ---- USUARIOS DJANGO ----
users_qs = list(User.objects.filter(is_active=True).exclude(email='').exclude(email__icontains='@example.com'))
users_items = [(u.first_name or u.username, u.email) for u in users_qs]

sent_u, errors_u = send_batch(users_items, is_lead=False, label='ETAPA 2: usuarios cadastrados na plataforma')

print(f"\n{'='*50}", flush=True)
print("RESUMO FINAL:", flush=True)
print(f"  Leads CSV:  {sent_l} enviados, {errors_l} erros", flush=True)
print(f"  Usuarios:   {sent_u} enviados, {errors_u} erros", flush=True)
print(f"  TOTAL:      {sent_l + sent_u} enviados", flush=True)
print(f"{'='*50}", flush=True)
