# Sistema de Pagamentos - Mercado Pago

## ✅ IMPLEMENTAÇÃO COMPLETA

Sistema de cobrança automática de R$ 49,99/mês para assinaturas de instrutores integrado com Mercado Pago.

---

## 📋 O QUE FOI IMPLEMENTADO

### 1. Modelo Payment (`billing/models.py`)
- **Campos principais:**
  - `subscription` (FK para Subscription)
  - `amount` (Decimal - valor pago)
  - `payment_method` (PIX/BOLETO/CREDIT_CARD/DEBIT_CARD)
  - `status` (PENDING/APPROVED/REJECTED/CANCELLED/REFUNDED)
  - `external_id` (ID do pagamento no Mercado Pago - único)
  - `preference_id` (ID da preferência criada)
  - `paid_at` (Data/hora do pagamento aprovado)
  - `payment_details` (JSON com resposta completa do MP)

### 2. Views de Pagamento (`billing/views.py`)

#### `checkout_view(request, subscription_id)`
- Cria preferência de pagamento no Mercado Pago
- Gera botão checkout com PIX/Boleto/Cartão
- Salva Payment record com status PENDING
- Redireciona para página de checkout

#### `mercadopago_webhook(request)`
- Recebe notificações do Mercado Pago (payment.created, payment.updated)
- Busca detalhes do pagamento via API
- Atualiza status do Payment
- **Se aprovado:** Estende `subscription.end_date` por +30 dias
- Ativa subscription automaticamente

#### URLs de retorno
- `/pagamento/sucesso/` - Redireciona para dashboard com mensagem de sucesso
- `/pagamento/falha/` - Permite tentar novamente
- `/pagamento/pendente/` - Informa que pagamento está sendo processado

### 3. Template de Checkout (`templates/billing/checkout.html`)
- Informações do plano e valor
- Botão Mercado Pago (carrega SDK automaticamente)
- Opções visuais: PIX, Cartão, Boleto
- Badge de segurança
- Botão voltar

### 4. Template Assinatura Atualizado (`templates/billing/my_subscription.html`)
- **Alerta de expiração:** Mostra aviso 3 dias antes
- **Botão renovar:** Link direto para `/planos/checkout/<subscription_id>/`
- **Status expirado:** Alerta vermelho com botão urgente

### 5. Admin Django (`billing/admin.py`)
- PaymentAdmin com todos os campos readonly
- Visualização de `external_id`, instrutor, valor, método, status
- Filtros por status, método, data
- Busca por ID externo, preferência, nome do instrutor

### 6. Configurações (`config/settings.py`)
```python
MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY', default='')
MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN', default='')
```

### 7. Credenciais (`.env.mercadopago` - NÃO COMMITAR)
```bash
MERCADOPAGO_PUBLIC_KEY=APP_USR-2c64879c-db66-4546-a8ba-f9daa7851269
MERCADOPAGO_ACCESS_TOKEN=APP_USR-252257382533300-011222-d7003683caae3927fb199a49ab7fd0a4-3130461427
```

⚠️ **ATENÇÃO:** Estas são credenciais de **PRODUÇÃO** (APP_USR-), não de teste!

### 8. Script de Instalação (`scripts/install_payment_system.sh`)
```bash
chmod +x scripts/install_payment_system.sh
ssh root@72.61.36.89
cd /var/www/TREINACNH
./scripts/install_payment_system.sh
```

### 9. Comando Django (`billing/management/commands/check_expiring_subscriptions.py`)
```bash
python manage.py check_expiring_subscriptions
```
- Verifica assinaturas expirando em 3 dias
- Lista assinaturas já expiradas
- **TODO:** Enviar emails automáticos (descomentar send_email)

---

## 🚀 COMO USAR NO SERVIDOR

### Passo 1: Upload dos arquivos
```bash
# No Windows (seu computador)
git add .
git commit -m "Sistema de pagamentos Mercado Pago completo"
git push origin main
```

### Passo 2: Atualizar servidor
```bash
ssh root@72.61.36.89
cd /var/www/TREINACNH
git pull origin main
```

### Passo 3: Executar instalação
```bash
chmod +x scripts/install_payment_system.sh
./scripts/install_payment_system.sh
```

O script irá:
1. ✅ Instalar `mercadopago==2.2.3`
2. ✅ Adicionar credenciais ao `.env`
3. ✅ Criar migrations do modelo Payment
4. ✅ Aplicar migrations
5. ✅ Coletar arquivos estáticos
6. ✅ Reiniciar Gunicorn

---

## 🔔 CONFIGURAR WEBHOOK NO MERCADO PAGO

### Acesse o Painel:
https://www.mercadopago.com.br/developers/panel/app

### Configurações → Webhooks
1. **URL de notificações:** `http://72.61.36.89:8080/webhook/mercadopago/`
2. **Eventos selecionados:**
   - ✅ `payment.created`
   - ✅ `payment.updated`
3. **Salvar**

### Testar Webhook
No painel do Mercado Pago:
- Enviar notificação de teste
- Verificar logs: `tail -f /var/www/TREINACNH/logs/django.log`

---

## 💳 FLUXO COMPLETO DE PAGAMENTO

```
1. INSTRUTOR acessa "Minha Assinatura"
   ↓
2. Vê alerta: "Sua assinatura expira em 3 dias"
   ↓
3. Clica "Renovar Assinatura"
   ↓
4. Sistema cria Preference no Mercado Pago
   ↓
5. Botão "Pagar com Mercado Pago" aparece
   ↓
6. Instrutor escolhe: PIX / Boleto / Cartão
   ↓
7. Realiza pagamento
   ↓
8. Mercado Pago envia webhook para servidor
   ↓
9. Sistema recebe notification → busca payment details
   ↓
10. Se status == 'approved':
    - Payment.status = APPROVED
    - Payment.paid_at = agora
    - Subscription.end_date += 30 dias
    - Subscription.status = ACTIVE
    ↓
11. Instrutor redirecionado para "Pagamento Aprovado"
    ↓
12. Sistema envia email de confirmação (TODO)
```

---

## 🧪 COMO TESTAR

### 1. Criar Assinatura de Teste
Acesse admin Django:
http://72.61.36.89:8080/admin/billing/subscription/add/

- **Instrutor:** Selecione um instrutor existente
- **Plano:** Selecione plano ativo
- **Status:** ACTIVE
- **Data início:** Hoje
- **Data término:** Hoje + 3 dias (para testar alerta)

### 2. Fazer Login como Instrutor
```
http://72.61.36.89:8080/contas/login/
```

### 3. Acessar Minha Assinatura
```
http://72.61.36.89:8080/planos/minha-assinatura/
```
- Deve aparecer alerta amarelo: "Expira em 3 dias"
- Botão "Renovar Assinatura"

### 4. Clicar Renovar
- Abre página checkout
- Botão Mercado Pago carrega
- Opções: PIX, Cartão, Boleto

### 5. Pagar com Cartão de Teste (PRODUÇÃO)
⚠️ **Como são credenciais de produção, pagamentos reais serão cobrados!**

**Opções:**
- Usar cartão real (será cobrado de verdade)
- Solicitar credenciais de **TESTE** no Mercado Pago para testes seguros

### Cartões de Teste (só funcionam em modo TESTE):
```
Aprovado: 5031 4332 1540 6351
Nome: APRO
CVV: 123
Validade: 11/25

Rejeitado: 5031 4332 1540 6351
Nome: OTHE
```

---

## 📧 EMAILS AUTOMÁTICOS (TODO)

### Implementar em `billing/emails.py`:

#### 1. Email de Aviso (3 dias antes)
```python
def send_expiration_warning_email(to_email, instructor_name, plan_name, expiration_date, renewal_url):
    subject = f"⚠️ {instructor_name}, sua assinatura expira em 3 dias!"
    message = f"""
    Olá {instructor_name},
    
    Sua assinatura do plano {plan_name} expira em {expiration_date}.
    
    Renove agora para continuar visível no TreinaCNH:
    {renewal_url}
    
    Qualquer dúvida, estamos à disposição.
    
    Equipe TreinaCNH
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
```

#### 2. Email de Confirmação (após pagamento)
```python
def send_payment_confirmation_email(subscription, payment):
    user = subscription.instructor.user
    subject = "✅ Pagamento Confirmado - TreinaCNH"
    message = f"""
    Olá {user.get_full_name()},
    
    Seu pagamento de R$ {payment.amount} foi confirmado!
    
    Plano: {subscription.plan.name}
    Válido até: {subscription.end_date}
    Método: {payment.get_payment_method_display()}
    
    Obrigado por confiar no TreinaCNH!
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
```

#### 3. Configurar Cron para Verificação Diária
```bash
crontab -e
```
Adicionar:
```
0 9 * * * cd /var/www/TREINACNH && venv/bin/python manage.py check_expiring_subscriptions
```

---

## 🔒 SEGURANÇA

### 1. Credenciais NO .env (NÃO commitar)
✅ Arquivo `.env.mercadopago` criado localmente
✅ Não está no `.gitignore`? Adicionar:
```bash
echo ".env.mercadopago" >> .gitignore
```

### 2. Webhook sem CSRF
✅ Decorator `@csrf_exempt` no webhook (Mercado Pago não envia token)
✅ Validação de `external_reference` para evitar fraudes

### 3. HTTPS Recomendado
⚠️ Webhook em HTTP funciona mas é menos seguro
🔒 Configurar HTTPS com Certbot (Let's Encrypt) para produção

---

## 📊 MONITORAMENTO

### Ver Logs do Webhook
```bash
tail -f /var/www/TREINACNH/logs/django.log | grep "Webhook"
```

### Ver Pagamentos no Admin
http://72.61.36.89:8080/admin/billing/payment/

### Testar Webhook Manualmente
```bash
curl -X POST http://72.61.36.89:8080/webhook/mercadopago/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "123456789"
    }
  }'
```

---

## ❗ AVISOS IMPORTANTES

1. **CREDENCIAIS DE PRODUÇÃO**
   - São credenciais reais, não de teste
   - Pagamentos serão cobrados de verdade
   - Para testes seguros, solicite credenciais TEST no MP

2. **WEBHOOK PÚBLICO**
   - URL http://72.61.36.89:8080/webhook/mercadopago/ deve estar acessível
   - Não bloquear no firewall
   - Configurar no painel do Mercado Pago

3. **EMAILS**
   - Código comentado com `# TODO: send_email`
   - Descomentar após configurar SMTP no `settings.py`

4. **HTTPS**
   - Altamente recomendado para produção
   - Mercado Pago aceita HTTP mas prefere HTTPS

---

## 🆘 TROUBLESHOOTING

### Erro: "Preference creation failed"
- Verificar credenciais no `.env`
- Testar access token:
```bash
curl -X GET \
  'https://api.mercadopago.com/v1/payment_methods' \
  -H 'Authorization: Bearer APP_USR-252257382533300-011222-d7003683caae3927fb199a49ab7fd0a4-3130461427'
```

### Webhook não recebe notificações
- Verificar URL no painel MP
- Testar acessibilidade: `curl http://72.61.36.89:8080/webhook/mercadopago/`
- Ver logs: `tail -f logs/django.log`

### Pagamento aprovado mas assinatura não renovou
- Verificar logs do webhook
- Verificar `external_reference` no payment
- Rodar manualmente:
```python
python manage.py shell
from billing.models import Payment, Subscription
from datetime import timedelta
from django.utils import timezone

payment = Payment.objects.get(external_id='MP_ID_AQUI')
sub = payment.subscription
sub.end_date = sub.end_date + timedelta(days=30)
sub.status = 'ACTIVE'
sub.save()
```

---

## 📞 SUPORTE

Documentação oficial Mercado Pago:
https://www.mercadopago.com.br/developers/pt/docs

SDKs e APIs:
https://www.mercadopago.com.br/developers/pt/docs/sdks-library/server-side

Painel de desenvolvedor:
https://www.mercadopago.com.br/developers/panel/app

---

**Sistema pronto para deploy! 🚀**
