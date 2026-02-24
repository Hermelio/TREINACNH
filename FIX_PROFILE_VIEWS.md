# Fix: Erro 500 no Painel do Instrutor

## Problema Identificado

**Erro:** `AttributeError: 'InstructorProfile' object has no attribute 'profile_views'`

**Local:** `/marketplace/meus-leads/`

**Causa:** O campo `profile_views` foi adicionado ao modelo `InstructorProfile` no código, mas não existia no banco de dados de produção.

## Solução Aplicada

### 1. Identificação do Erro
```bash
tail -n 100 /var/www/TREINACNH/logs/django.log
```

**Log do Erro:**
```
ERROR 2026-02-22 19:23:49,684 log Internal Server Error: /instrutores/meus-leads/
AttributeError: 'InstructorProfile' object has no attribute 'profile_views'
```

### 2. Tentativa de Migration (Falhou)
Tentamos executar `makemigrations` mas havia um arquivo de migration corrompido com null bytes:
```
SyntaxError: source code string cannot contain null bytes
```

### 3. Solução: Adicionar Campo Diretamente no Banco

Como as migrations estavam corrompidas, adicionamos o campo diretamente via SQL:

```bash
mysql -u integrador -p'Crystal@comgas2024!' treinacnh -e \
'ALTER TABLE marketplace_instructorprofile ADD COLUMN profile_views INTEGER NOT NULL DEFAULT 0;'
```

### 4. Verificação
```bash
mysql -u integrador -p'Crystal@comgas2024!' treinacnh -e \
'SELECT COUNT(*), profile_views FROM marketplace_instructorprofile GROUP BY profile_views;'
```

**Resultado:** 34 instrutores com profile_views = 0 ✓

### 5. Reiniciar Serviço
```bash
systemctl restart gunicorn-treinacnh
```

## Status Final

✅ **Campo criado:** `profile_views INTEGER NOT NULL DEFAULT 0`  
✅ **Gunicorn reiniciado:** 22:26:21 UTC  
✅ **Erro resolvido:** Painel do instrutor funcionando  

## Teste Realizado

- Acesso ao painel: `/marketplace/meus-leads/`
- Status: **200 OK**
- Dashboard exibindo:
  - Perfil Profissional ✓
  - Visualizações do Perfil ✓
  - Contatos WhatsApp ✓

## Próximos Passos

1. Resolver problema das migrations corrompidas
2. Criar migration limpa para o campo `profile_views`
3. Verificar se há outros campos faltando no banco de produção

## Data do Fix

**22/02/2026 - 22:26 UTC**
