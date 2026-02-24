# Executa após configurar a App Password no .env do servidor.
# Uso: .\test_smtp_after_apppassword.ps1
# Nenhuma credencial é armazenada neste script.

$test = @'
import sys
from django.conf import settings
from django.core.mail import send_mail

print("=== CONFIG ATIVA ===")
print(f"  BACKEND:  {settings.EMAIL_BACKEND}")
print(f"  HOST:     {settings.EMAIL_HOST}:{settings.EMAIL_PORT} TLS={settings.EMAIL_USE_TLS}")
print(f"  USER:     {settings.EMAIL_HOST_USER}")
print(f"  FROM:     {settings.DEFAULT_FROM_EMAIL}")
print(f"  TIMEOUT:  {settings.PASSWORD_RESET_TIMEOUT}s ({settings.PASSWORD_RESET_TIMEOUT//3600}h)")
print()
print("=== ENVIANDO E-MAIL DE TESTE ===")

try:
    n = send_mail(
        subject="[TreinaCNH] SMTP OK - Teste de envio",
        message=(
            "Parabens! O envio de e-mails via Gmail SMTP esta funcionando.\n\n"
            "Isso significa que o fluxo 'Esqueci minha senha' esta pronto para producao.\n\n"
            "Servidor: 72.61.36.89\n"
            "Dominio: https://treinacnh.com.br\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print(f"  send_mail() = {n}  (1 = sucesso)")
    print()
    print("RESULTADO: EMAIL ENVIADO COM SUCESSO")
    print("Verifique a caixa de entrada de:", settings.EMAIL_HOST_USER)
except Exception as e:
    print(f"  ERRO: {type(e).__name__}: {e}")
    if "BadCredentials" in str(e) or "535" in str(e):
        print()
        print("  A App Password ainda nao foi configurada ou esta incorreta.")
        print("  Gere em: https://myaccount.google.com/apppasswords")
        print("  Atualize: sed -i 's|^EMAIL_HOST_PASSWORD=.*|EMAIL_HOST_PASSWORD=NOVA_APP_PW|' /var/www/TREINACNH/.env")
    sys.exit(1)
'@

$test | ssh root@72.61.36.89 "cat > /tmp/smtp_test.py && cd /var/www/TREINACNH && venv/bin/python manage.py shell < /tmp/smtp_test.py 2>&1"
