#!/usr/bin/env python
"""
Envio de emails em blocos para evitar bloqueio do Gmail.
Salva progresso em /var/www/TREINACNH/email_progress.json
Cada execucao envia BATCH_SIZE emails e para.
Agendar via cron: a cada 2 horas.

Cron (como root): 55 1,3,5,7,9,11,13,15,17,19,21,23 * * * cd /var/www/TREINACNH && source venv/bin/activate && python -u batch_send_emails.py >> /var/log/treinacnh_batch_email.log 2>&1
"""
import os, sys, django, time, json
sys.path.insert(0, '/var/www/TREINACNH')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from marketplace.models import StudentLead
from django.core.mail import get_connection, EmailMultiAlternatives, send_mail
from django.conf import settings
from datetime import datetime

SITE_URL = 'http://72.61.36.89:8080'
RESET_URL = f'{SITE_URL}/contas/senha/recuperar/'
REGISTER_URL = f'{SITE_URL}/contas/registrar/'
NOTIFY_EMAIL = 'treinacnh@gmail.com'

BATCH_SIZE = 40
DELAY = 4
PROGRESS_FILE = '/var/www/TREINACNH/email_progress.json'


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def notify_admin(sent_now, errors_now, total_sent, total_all, done=False):
    """Envia email de confirmacao para o admin apos cada bloco."""
    remaining = total_all - total_sent
    pct = round((total_sent / total_all) * 100, 1) if total_all > 0 else 0

    if done:
        subject = '✅ TreinaCNH - Todos os emails foram enviados!'
        body = f"""Parabens! O envio foi concluido com sucesso.

Total enviado: {total_sent}/{total_all} emails (100%)

Equipe TreinaCNH"""
    else:
        subject = f'📧 TreinaCNH - Bloco enviado: {total_sent}/{total_all} ({pct}%)'
        body = f"""Bloco de emails enviado com sucesso.

Neste bloco: {sent_now} enviados, {errors_now} erros
Total acumulado: {total_sent}/{total_all} ({pct}%)
Faltam: {remaining} emails

Proximo bloco sera enviado automaticamente em ~2 horas.

Equipe TreinaCNH"""

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[NOTIFY_EMAIL],
            fail_silently=True,
        )
        log(f"Confirmacao enviada para {NOTIFY_EMAIL}")
    except Exception as e:
        log(f"Nao foi possivel enviar confirmacao: {e}")


def build_html(name, is_lead=False, email=''):
    action_block = f"""
            <div class="highlight">
                <strong>&#9888; ACAO NECESSARIA:</strong> Finalize seu cadastro na nova plataforma.
            </div>
            <h2>Como acessar:</h2>
            <ol>
                <li>Acesse o link abaixo e crie sua conta</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Complete seu perfil e aproveite gratuitamente!</li>
            </ol>
            <center><a href="{REGISTER_URL}" class="button">Finalizar Meu Cadastro</a></center>
""" if is_lead else f"""
            <div class="highlight">
                <strong>&#9888; ACAO NECESSARIA:</strong> Redefina sua senha para acessar a nova plataforma.
            </div>
            <h2>Como acessar:</h2>
            <ol>
                <li>Acesse o link abaixo para redefinir sua senha</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Crie uma nova senha e faca login</li>
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
                <li>Busca de instrutores por cidade e estado</li>
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


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'sent': [], 'done': False}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def build_all_recipients():
    existing_emails = set(User.objects.exclude(email='').values_list('email', flat=True))
    leads = [l for l in StudentLead.objects.filter(accept_email=True).exclude(email='')
             if l.email.lower() not in {e.lower() for e in existing_emails}]
    users = list(User.objects.filter(is_active=True)
                 .exclude(email='').exclude(email__icontains='@example.com'))
    all_recipients = []
    for l in leads:
        all_recipients.append((l.name.split()[0] if l.name else 'Aluno', l.email, True))
    for u in users:
        all_recipients.append((u.first_name or u.username, u.email, False))
    return all_recipients


# ---- MAIN ----
progress = load_progress()

if progress.get('done'):
    log("Todos os emails ja foram enviados. Nada a fazer.")
    sys.exit(0)

sent_set = set(e.lower() for e in progress['sent'])
all_recipients = build_all_recipients()
pending = [(n, e, il) for n, e, il in all_recipients if e.lower() not in sent_set]
total_pending = len(pending)
total_all = len(all_recipients)

log(f"Pendentes: {total_pending} / Total: {total_all} / Ja enviados: {len(sent_set)}")

if total_pending == 0:
    progress['done'] = True
    save_progress(progress)
    log("Todos os emails foram enviados!")
    notify_admin(0, 0, len(sent_set), total_all, done=True)
    sys.exit(0)

batch = pending[:BATCH_SIZE]
log(f"Enviando bloco de {len(batch)} emails...")

connection = get_connection()
try:
    connection.open()
    log("Conexao SMTP aberta.")
except Exception as e:
    log(f"ERRO ao abrir conexao SMTP: {e}")
    sys.exit(1)

sent_now = 0
errors_now = 0

for i, (name, email, is_lead) in enumerate(batch, 1):
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
        sent_now += 1
        progress['sent'].append(email)
        save_progress(progress)
        log(f"  OK {i}/{len(batch)} [{len(progress['sent'])}/{total_all}] {email}")
        time.sleep(DELAY)
    except Exception as e:
        errors_now += 1
        log(f"  ERRO {email}: {e}")
        try:
            connection.close()
            time.sleep(15)
            connection.open()
            log("  Conexao SMTP reaberta.")
        except Exception as e2:
            log(f"  Falha ao reabrir conexao: {e2}")

try:
    connection.close()
except Exception:
    pass

total_sent_now = len(progress['sent'])
remaining = total_all - total_sent_now

if remaining <= 0:
    progress['done'] = True
    save_progress(progress)
    log("CONCLUIDO! Todos os emails foram enviados.")
    notify_admin(sent_now, errors_now, total_sent_now, total_all, done=True)
else:
    log(f"Bloco concluido. Faltam ~{remaining} emails. Proximo bloco em ~2 horas.")
    notify_admin(sent_now, errors_now, total_sent_now, total_all, done=False)

log(f"Resumo deste bloco: {sent_now} enviados, {errors_now} erros.")

import os, sys, django, time, json
sys.path.insert(0, '/var/www/TREINACNH')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from marketplace.models import StudentLead
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings
from datetime import datetime

SITE_URL = 'http://72.61.36.89:8080'
RESET_URL = f'{SITE_URL}/contas/senha/recuperar/'
REGISTER_URL = f'{SITE_URL}/contas/registrar/'

BATCH_SIZE = 40       # emails por execucao
DELAY = 4             # segundos entre cada email
PROGRESS_FILE = '/var/www/TREINACNH/email_progress.json'


def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def build_html(name, is_lead=False, email=''):
    action_block = f"""
            <div class="highlight">
                <strong>&#9888; ACAO NECESSARIA:</strong> Finalize seu cadastro na nova plataforma.
            </div>
            <h2>Como acessar:</h2>
            <ol>
                <li>Acesse o link abaixo e crie sua conta</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Complete seu perfil e aproveite gratuitamente!</li>
            </ol>
            <center><a href="{REGISTER_URL}" class="button">Finalizar Meu Cadastro</a></center>
""" if is_lead else f"""
            <div class="highlight">
                <strong>&#9888; ACAO NECESSARIA:</strong> Redefina sua senha para acessar a nova plataforma.
            </div>
            <h2>Como acessar:</h2>
            <ol>
                <li>Acesse o link abaixo para redefinir sua senha</li>
                <li>Use o email: <strong>{email}</strong></li>
                <li>Crie uma nova senha e faca login</li>
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
                <li>Busca de instrutores por cidade e estado</li>
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


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'sent': [], 'done': False}


def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)


def build_all_recipients():
    """Monta lista completa: (name, email, is_lead) de leads + usuarios."""
    existing_emails = set(User.objects.exclude(email='').values_list('email', flat=True))

    leads = [l for l in StudentLead.objects.filter(accept_email=True).exclude(email='')
             if l.email.lower() not in {e.lower() for e in existing_emails}]

    users = list(User.objects.filter(is_active=True)
                 .exclude(email='')
                 .exclude(email__icontains='@example.com'))

    all_recipients = []
    for l in leads:
        all_recipients.append((l.name.split()[0] if l.name else 'Aluno', l.email, True))
    for u in users:
        all_recipients.append((u.first_name or u.username, u.email, False))

    return all_recipients


# ---- MAIN ----
progress = load_progress()

if progress.get('done'):
    log("Todos os emails ja foram enviados. Nada a fazer.")
    sys.exit(0)

sent_set = set(e.lower() for e in progress['sent'])
all_recipients = build_all_recipients()
pending = [(n, e, il) for n, e, il in all_recipients if e.lower() not in sent_set]
total_pending = len(pending)
total_all = len(all_recipients)

log(f"Pendentes: {total_pending} / Total: {total_all} / Ja enviados: {len(sent_set)}")

if total_pending == 0:
    progress['done'] = True
    save_progress(progress)
    log("Todos os emails foram enviados!")
    sys.exit(0)

batch = pending[:BATCH_SIZE]
log(f"Enviando bloco de {len(batch)} emails...")

connection = get_connection()
try:
    connection.open()
    log("Conexao SMTP aberta.")
except Exception as e:
    log(f"ERRO ao abrir conexao SMTP: {e}")
    sys.exit(1)

sent_now = 0
errors_now = 0

for i, (name, email, is_lead) in enumerate(batch, 1):
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
        sent_now += 1
        progress['sent'].append(email)
        save_progress(progress)
        log(f"  OK {i}/{len(batch)} [{len(progress['sent'])}/{total_all}] {email}")
        time.sleep(DELAY)
    except Exception as e:
        errors_now += 1
        log(f"  ERRO {email}: {e}")
        try:
            connection.close()
            time.sleep(15)
            connection.open()
            log("  Conexao SMTP reaberta.")
        except Exception as e2:
            log(f"  Falha ao reabrir conexao: {e2}")

try:
    connection.close()
except Exception:
    pass

# Marca como concluido se nao ha mais pendentes
remaining = total_pending - len(batch)
if remaining <= 0:
    progress['done'] = True
    save_progress(progress)
    log("CONCLUIDO! Todos os emails foram enviados.")
else:
    log(f"Bloco concluido. Faltam ~{remaining} emails. Proximo bloco na proxima execucao do cron.")

log(f"Resumo deste bloco: {sent_now} enviados, {errors_now} erros.")
