# 🎯 PRÓXIMOS PASSOS - Login com Google

## ✅ O QUE JÁ ESTÁ PRONTO

- ✅ django-allauth instalado no servidor
- ✅ Migrations executadas com sucesso
- ✅ Serviço TREINACNH reiniciado
- ✅ COMCURSANDO não foi afetado (continua rodando)
- ✅ Templates com botões do Google prontos
- ✅ OAuth 2.0 criado no Google Cloud Console

---

## 📋 CONFIGURAÇÃO FINAL (10 minutos)

### 1. Adicionar Credenciais Google ao .env do Servidor

```bash
ssh root@72.61.36.89
cd /var/www/TREINACNH
nano .env
```

**Adicionar estas linhas:**
```env
GOOGLE_CLIENT_ID=seu_client_id_aqui.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-seu_secret_aqui
```

Salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

**Reiniciar serviço:**
```bash
systemctl restart gunicorn-treinacnh.service
```

---

### 2. Configurar Site no Admin Django

1. Acesse: `http://72.61.36.89:8080/admin/`
2. Faça login como admin
3. Vá em **Sites > Sites**
4. Edite o site com **ID = 1**:
   - **Domain name**: `72.61.36.89:8080` (ou `treinacnh.com.br` se tiver domínio)
   - **Display name**: `TREINACNH`
5. Clique em **Save**

---

### 3. Adicionar Google OAuth no Admin

1. No admin, vá em **Social accounts > Social applications**
2. Clique em **Add Social Application** (botão verde no canto superior direito)
3. Preencha:
   - **Provider**: Selecione `Google`
   - **Name**: `Google OAuth`
   - **Client id**: Cole o Client ID do Google Cloud Console
   - **Secret key**: Cole o Client Secret do Google Cloud Console
   - **Key**: Deixe em branco
4. Em **Sites** (no final da página):
   - Selecione o site `72.61.36.89:8080` ou `treinacnh.com.br`
   - Clique na seta `→` para mover para **Chosen sites**
5. Clique em **Save**

---

## 🧪 TESTAR O LOGIN COM GOOGLE

### Teste Local (se quiser):
1. Acesse: `http://localhost:8000/contas/login/`
2. Clique em **"Continuar com Google"**
3. Faça login com sua conta Google
4. Deve redirecionar para o dashboard

### Teste no Servidor:
1. Acesse: `http://72.61.36.89:8080/contas/login/`
2. Clique em **"Continuar com Google"**
3. Faça login com sua conta Google
4. Deve redirecionar para o dashboard

---

## ✅ CHECKLIST DE VERIFICAÇÃO

Após configurar, verifique se:

- [ ] Botão "Continuar com Google" aparece na página de login
- [ ] Botão "Cadastrar com Google" aparece na página de registro
- [ ] Ao clicar no botão, abre a tela de login do Google
- [ ] Após login no Google, redireciona para o dashboard
- [ ] Novo usuário é criado no Django Admin
- [ ] Profile do usuário é criado automaticamente
- [ ] E-mail do Google é salvo corretamente

---

## 🐛 TROUBLESHOOTING

### Erro: "Site matching query does not exist"
**Causa**: Site não foi configurado no admin  
**Solução**: Siga o passo 2 acima

### Erro: "SocialApp matching query does not exist"
**Causa**: Google OAuth não foi adicionado no admin  
**Solução**: Siga o passo 3 acima

### Erro: "Redirect URI mismatch"
**Causa**: URI no Google Console diferente da configurada  
**Solução**: Verifique no Google Console se as URIs estão:
```
http://72.61.36.89:8080/contas/google/login/callback/
https://treinacnh.com.br/contas/google/login/callback/
```

### Botão do Google não aparece
**Causa**: Erro de template ou configuração  
**Solução**: Verifique os logs:
```bash
ssh root@72.61.36.89
tail -f /var/www/TREINACNH/logs/gunicorn-error.log
```

---

## 📊 VERIFICAR LOGS

```bash
# Logs do Gunicorn
ssh root@72.61.36.89
tail -f /var/www/TREINACNH/logs/gunicorn-error.log

# Status do serviço
systemctl status gunicorn-treinacnh.service
```

---

## 🎉 APÓS CONFIGURAR

O sistema estará 100% funcional com:

✅ Login tradicional (username/senha)  
✅ Login com Google (OAuth 2.0)  
✅ Cadastro tradicional (formulário completo)  
✅ Cadastro com Google (1 clique)  
✅ Profile criado automaticamente  
✅ E-mail já verificado pelo Google  

---

## 📞 DÚVIDAS?

Consulte o guia completo em: `GOOGLE_LOGIN_SETUP.md`
