#!/usr/bin/env python
"""
Teste do email de boas-vindas — envia UMA amostra de cada tipo para treinacnh@gmail.com
"""
import os, sys, django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.core.mail import send_mail
from django.conf import settings

TEST_EMAIL = 'treinacnh@gmail.com'

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


# --- Teste 1: email para aluno do CSV (lead) ---
print(f"Enviando teste 1/2 — versão ALUNO (lead CSV) para {TEST_EMAIL}...")
send_mail(
    subject='[TESTE] 🎉 Nova Plataforma TreinaCNH — Finalize seu Cadastro!',
    message=f'Olá João, finalize seu cadastro em {REGISTER_URL}',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[TEST_EMAIL],
    html_message=build_html('João (Lead CSV)', is_lead=True, email='joao@exemplo.com'),
    fail_silently=False,
)
print("✅ Enviado!")

# --- Teste 2: email para usuário já cadastrado ---
print(f"Enviando teste 2/2 — versão USUÁRIO CADASTRADO para {TEST_EMAIL}...")
send_mail(
    subject='[TESTE] 🎉 Nova Plataforma TreinaCNH — Acesse Sua Conta!',
    message=f'Olá Carlos, redefina sua senha em {RESET_URL}',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[TEST_EMAIL],
    html_message=build_html('Carlos (Usuário Cadastrado)', is_lead=False, email='carlos@exemplo.com'),
    fail_silently=False,
)
print("✅ Enviado!")

print("\n✅ Ambos os emails de teste enviados para", TEST_EMAIL)
