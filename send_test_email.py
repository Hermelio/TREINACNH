#!/usr/bin/env python
"""
Script de TESTE - Envia email apenas para o administrador para visualização.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/var/www/TREINACNH')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

def send_test_email():
    """
    Envia email de teste para o primeiro admin ou superuser.
    """
    # Buscar admin
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user or not admin_user.email:
        print("❌ Nenhum superuser com email encontrado")
        return
    
    print(f"\n📧 Enviando email de TESTE para: {admin_user.email}")
    print("=" * 60)
    
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
        .test-banner {{ background: #dc3545; color: white; padding: 10px; text-align: center; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="test-banner">
        ⚠️ ESTE É UM EMAIL DE TESTE - NÃO FOI ENVIADO PARA USUÁRIOS
    </div>
    <div class="container">
        <div class="header">
            <h1>🚗 Bem-vindo à Nova TreinaCNH!</h1>
        </div>
        <div class="content">
            <p>Olá <strong>[NOME DO USUÁRIO]</strong>,</p>
            
            <p>Estamos muito felizes em tê-lo(a) conosco! A plataforma <strong>TreinaCNH</strong> foi completamente renovada para oferecer a melhor experiência para conectar instrutores autônomos e alunos.</p>
            
            <div class="highlight">
                <strong>⚠️ AÇÃO NECESSÁRIA:</strong> Como migramos nossa plataforma, você precisa redefinir sua senha para acessar sua conta.
            </div>
            
            <h2>🔑 Como acessar sua conta:</h2>
            <ol>
                <li>Clique no botão abaixo para recuperar sua senha</li>
                <li>Digite seu email: <strong>[EMAIL DO USUÁRIO]</strong></li>
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
    
    plain_message = """
⚠️ ESTE É UM EMAIL DE TESTE - NÃO FOI ENVIADO PARA USUÁRIOS

Olá [NOME DO USUÁRIO],

Estamos muito felizes em tê-lo(a) conosco! A plataforma TreinaCNH foi completamente renovada.

⚠️ AÇÃO NECESSÁRIA: 
Como migramos nossa plataforma, você precisa redefinir sua senha para acessar sua conta.

🔑 Como acessar sua conta:
1. Acesse: https://treinacnh.com.br/accounts/password-reset/
2. Digite seu email: [EMAIL DO USUÁRIO]
3. Você receberá um link para criar uma nova senha
4. Faça login e complete seu perfil

Se você tiver qualquer dúvida, estamos à disposição!

Atenciosamente,
Equipe TreinaCNH
"""
    
    try:
        send_mail(
            subject='[TESTE] 🎉 Bem-vindo à Nova Plataforma TreinaCNH',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"✅ Email de teste enviado para: {admin_user.email}")
        print("\n📋 Verifique sua caixa de entrada e veja como o email ficou!")
        print("    Se estiver bom, execute o script principal: send_welcome_email.py")
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("   TESTE DE EMAIL - TREINACNH")
    print("=" * 60)
    send_test_email()
