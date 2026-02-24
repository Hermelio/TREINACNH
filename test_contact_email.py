"""
Script para testar o envio de email do formulário de contato.
Uso: python manage.py shell < test_contact_email.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 60)
print("TESTE DE ENVIO DE EMAIL - FORMULÁRIO DE CONTATO")
print("=" * 60)
print("\n=== CONFIGURAÇÃO ATUAL DE EMAIL ===")
print(f"Backend:       {settings.EMAIL_BACKEND}")
print(f"Host:          {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"Use TLS:       {settings.EMAIL_USE_TLS}")
print(f"Use SSL:       {settings.EMAIL_USE_SSL}")
print(f"User:          {settings.EMAIL_HOST_USER or '(não configurado)'}")
print(f"Password:      {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(não configurado)'}")
print(f"From:          {settings.DEFAULT_FROM_EMAIL}")
print()

# Verifica se o backend é console (desenvolvimento)
if 'console' in settings.EMAIL_BACKEND.lower():
    print("⚠️  ATENÇÃO: EMAIL_BACKEND está configurado como 'console'")
    print("   Os emails não serão enviados, apenas exibidos no terminal.")
    print()
    print("   Para enviar emails reais, adicione ao arquivo .env:")
    print("   ---")
    print("   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
    print("   EMAIL_HOST=smtp.gmail.com")
    print("   EMAIL_PORT=587")
    print("   EMAIL_USE_TLS=True")
    print("   EMAIL_HOST_USER=treinacnh@gmail.com")
    print("   EMAIL_HOST_PASSWORD=sua_app_password_aqui")
    print("   DEFAULT_FROM_EMAIL=TreinaCNH <treinacnh@gmail.com>")
    print("   ---")
    print()
    print("   Como obter uma App Password do Gmail:")
    print("   1. Acesse: https://myaccount.google.com/apppasswords")
    print("   2. Entre com a conta treinacnh@gmail.com")
    print("   3. Digite um nome para o app (ex: 'Django TreinaCNH')")
    print("   4. Copie a senha gerada (16 caracteres)")
    print("   5. Cole no .env na variável EMAIL_HOST_PASSWORD")
    print()

# Tenta enviar um email de teste
print("=== ENVIANDO EMAIL DE TESTE ===")
print("Destinatário: treinacnh@gmail.com")
print()

try:
    num_sent = send_mail(
        subject="[CONTATO] Teste do Sistema - Por favor ignore",
        message="""
Nova mensagem de contato recebida através do site TreinaCNH:

Nome: Teste Automático
E-mail: teste@exemplo.com
Assunto: Teste do Sistema - Por favor ignore

Mensagem:
Esta é uma mensagem de teste para verificar se o sistema de envio de emails
do formulário de contato está funcionando corretamente.

Se você recebeu este email na caixa de entrada de treinacnh@gmail.com,
significa que o sistema está funcionando perfeitamente!

---
Esta mensagem foi enviada através do formulário de contato do site.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['treinacnh@gmail.com'],
        fail_silently=False,
    )
    
    print(f"✅ EMAIL ENVIADO COM SUCESSO!")
    print(f"   Número de emails enviados: {num_sent}")
    print()
    
    if 'console' in settings.EMAIL_BACKEND.lower():
        print("📧 O email foi exibido acima (backend console).")
        print("   Para enviar emails reais, configure o SMTP no .env")
    else:
        print("📬 Verifique a caixa de entrada de: treinacnh@gmail.com")
        print("   O email pode levar alguns segundos para chegar.")
    
except Exception as e:
    print(f"❌ ERRO AO ENVIAR EMAIL:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Mensagem: {e}")
    print()
    
    if "BadCredentials" in str(e) or "535" in str(e):
        print("   Causa provável: Email/senha incorretos ou App Password não configurada")
        print("   Solução: Verifique EMAIL_HOST_USER e EMAIL_HOST_PASSWORD no .env")
    elif "Connection" in str(e) or "timed out" in str(e):
        print("   Causa provável: Problema de conexão com o servidor SMTP")
        print("   Solução: Verifique sua conexão com a internet e as configurações do firewall")
    elif "550" in str(e):
        print("   Causa provável: O email remetente não corresponde ao usuário autenticado")
        print("   Solução: DEFAULT_FROM_EMAIL deve usar o mesmo email de EMAIL_HOST_USER")

print()
print("=" * 60)
