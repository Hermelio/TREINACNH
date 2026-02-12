# GUIA DE CONFIGURAÇÃO DO MERCADO PAGO
# =====================================

## 1. OBTER CREDENCIAIS

1. Acesse: https://www.mercadopago.com.br/developers/panel
2. Faça login com sua nova conta Mercado Pago
3. Vá em "Suas integrações" > Criar nova aplicação ou selecione existente
4. Vá em "Credenciais"
5. Escolha "Credenciais de produção" (para ambiente real)
6. Copie:
   - PUBLIC_KEY (começa com APP_USR-...)
   - ACCESS_TOKEN (começa com APP_USR-...)

## 2. ATUALIZAR CREDENCIAIS NO SERVIDOR

Execute no servidor:
```bash
cd /var/www/TREINACNH
bash update_mercadopago_credentials.sh
```

Ou manualmente, edite o arquivo .env:
```bash
nano /var/www/TREINACNH/.env
```

Adicione/atualize:
```
MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Salve e reinicie:
```bash
sudo systemctl restart treinacnh.service
```

## 3. CONFIGURAR WEBHOOK NO MERCADO PAGO

1. No painel do Mercado Pago: https://www.mercadopago.com.br/developers/panel
2. Vá em "Suas integrações" > Selecione sua aplicação
3. Vá em "Webhooks"
4. Clique em "Configurar webhooks"
5. Configure:
   - URL de notificação: http://72.61.36.89:8080/webhook/mercadopago/
   - Eventos a notificar: Selecione "Pagamentos"
6. Salve a configuração

## 4. CONFIGURAR MÉTODOS DE PAGAMENTO

No código já está configurado para aceitar:
- ✅ PIX (aprovação instantânea)
- ✅ Cartão de Crédito (até 12x)
- ✅ Cartão de Débito
- ❌ Boleto (removido da interface)

Para alterar métodos aceitos, edite billing/views.py:
```python
"payment_methods": {
    "excluded_payment_methods": [],  # IDs de métodos específicos a excluir
    "excluded_payment_types": [],    # Tipos a excluir (ex: "ticket" para boleto)
    "installments": 12,              # Máximo de parcelas
    "default_installments": 1        # Parcelas padrão
}
```

## 5. TESTAR PAGAMENTO

### Ambiente de Teste (Sandbox)
Use credenciais de teste e cartões de teste:
- Cartão aprovado: 5031 4332 1540 6351
- CVV: 123
- Data: qualquer data futura

### Ambiente de Produção
1. Faça login como instrutor no site
2. Vá em "Meus Planos"
3. Escolha um plano
4. Clique em "Pagar com Mercado Pago"
5. Será redirecionado para checkout do Mercado Pago
6. Escolha PIX ou Cartão de Crédito
7. Complete o pagamento

## 6. VERIFICAR LOGS

Ver logs de pagamento:
```bash
# Logs do Django
sudo journalctl -u treinacnh.service -f | grep -i "mercado\|payment\|webhook"

# Logs de pagamentos pendentes
cd /var/www/TREINACNH
source venv/bin/activate
python manage.py check_pending_payments
```

## 7. SOLUÇÃO DE PROBLEMAS

### Erro: "Credenciais inválidas"
- Verifique se copiou corretamente PUBLIC_KEY e ACCESS_TOKEN
- Certifique-se de usar credenciais de PRODUÇÃO (não teste)
- Verifique se reiniciou o serviço após alterar .env

### Webhook não recebe notificações
- Certifique-se que a URL está acessível: http://72.61.36.89:8080/webhook/mercadopago/
- Teste manualmente: curl -X POST http://72.61.36.89:8080/webhook/mercadopago/ -d '{}'
- Verifique logs: sudo journalctl -u treinacnh.service -f

### Pagamento não confirma
- Verifique se webhook está configurado no Mercado Pago
- Execute: python manage.py check_pending_payments
- Veja status no painel: https://www.mercadopago.com.br/activities

## 8. CONFIGURAÇÕES ADICIONAIS

### Personalizar nome na fatura
Edite billing/views.py:
```python
"statement_descriptor": "TREINACNH",  # Nome que aparece na fatura do cartão
```

### Alterar URL de retorno
Edite billing/views.py:
```python
"back_urls": {
    "success": f"{settings.SITE_URL}/billing/pagamento/sucesso/",
    "failure": f"{settings.SITE_URL}/billing/pagamento/falha/",
    "pending": f"{settings.SITE_URL}/billing/pagamento/pendente/"
}
```

### Limitar parcelas
```python
"installments": 6,  # Máximo 6x ao invés de 12x
```

## 9. MONITORAMENTO

Ver pagamentos no banco:
```bash
cd /var/www/TREINACNH
source venv/bin/activate
python manage.py shell
```
```python
from billing.models import Payment
Payment.objects.all().order_by('-created_at')[:10]
```

## 10. SUPORTE

- Documentação Mercado Pago: https://www.mercadopago.com.br/developers
- Suporte: https://www.mercadopago.com.br/developers/panel/support
- Status da API: https://status.mercadopago.com/
