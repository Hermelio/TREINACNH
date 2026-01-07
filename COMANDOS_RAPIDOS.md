# 🚀 Comandos Rápidos - TREINACNH

## 📡 Conectar ao Servidor
```powershell
ssh root@72.61.36.89
```

## 🔄 Deploy Rápido (Atualizar Código)
```powershell
ssh root@72.61.36.89 'cd /var/www/TREINACNH && git pull origin main && source venv/bin/activate && python manage.py migrate && python manage.py collectstatic --noinput && systemctl restart gunicorn-treinacnh'
```

## 🌐 Ver Site
- Produção: http://72.61.36.89:8080/
- Local: http://localhost:8000/

## 📊 Ver Logs em Tempo Real
```powershell
# Logs do Django
ssh root@72.61.36.89 'tail -f /var/www/TREINACNH/logs/django.log'

# Logs do Gunicorn
ssh root@72.61.36.89 'tail -f /var/www/TREINACNH/logs/gunicorn-error.log'

# Logs do Nginx
ssh root@72.61.36.89 'tail -f /var/log/nginx/error.log'
```

## 🔄 Reiniciar Serviços
```powershell
ssh root@72.61.36.89 'systemctl restart gunicorn-treinacnh && systemctl restart nginx'
```

## 💾 Backup do Banco
```powershell
# Criar backup
ssh root@72.61.36.89 "mysqldump -u integrador -p'Crystal@comgas2024!' treinacnh > /tmp/backup_$(date +%Y%m%d).sql"

# Baixar backup
scp root@72.61.36.89:/tmp/backup_*.sql ./backups/
```

## 🔍 Verificar Status
```powershell
# Status do Gunicorn
ssh root@72.61.36.89 'systemctl status gunicorn-treinacnh'

# Testar se site responde
ssh root@72.61.36.89 'curl -I http://127.0.0.1:8001/'
```

## 🗄️ MySQL Rápido
```powershell
# Conectar ao banco
ssh root@72.61.36.89 "mysql -u integrador -p'Crystal@comgas2024!' treinacnh"

# Ver tabelas
ssh root@72.61.36.89 "mysql -u integrador -p'Crystal@comgas2024!' treinacnh -e 'SHOW TABLES;'"
```

## 🎨 Atualizar Logo
```powershell
# Baixar nova logo
ssh root@72.61.36.89 'cd /var/www/TREINACNH/static/images && wget https://TreinaCNH.com.br/logo.png -O logo.png && cd ../.. && source venv/bin/activate && python manage.py collectstatic --noinput'
```

## 📝 Django Management
```powershell
# Criar superusuário
ssh root@72.61.36.89 'cd /var/www/TREINACNH && source venv/bin/activate && python manage.py createsuperuser'

# Executar migrações
ssh root@72.61.36.89 'cd /var/www/TREINACNH && source venv/bin/activate && python manage.py migrate'

# Shell Django
ssh root@72.61.36.89 'cd /var/www/TREINACNH && source venv/bin/activate && python manage.py shell'
```

## 💻 Desenvolvimento Local
```powershell
# Ativar ambiente virtual
& C:/Users/Windows/OneDrive/Documentos/PROJETOS/TREINACNH/venv/Scripts/Activate.ps1

# Rodar servidor
python manage.py runserver

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

## 📦 Git - Sincronizar
```powershell
# Ver status
git status

# Adicionar tudo
git add .

# Commit
git commit -m "descrição da mudança"

# Push
git push origin main

# Pull (atualizar local)
git pull origin main
```

## 🔐 Credenciais Importantes

**Servidor**
- IP: 72.61.36.89
- Usuário: root
- SSH: Chave configurada (sem senha)

**MySQL**
- Host: localhost
- Database: treinacnh
- User: integrador
- Password: Crystal@comgas2024!

**GitHub**
- Repo: https://github.com/Hermelio/TREINACNH

---

💡 **Dica**: Salve este arquivo nos favoritos para acesso rápido!

📚 **Documentação completa**: Ver [SERVIDOR_PRODUCAO.md](SERVIDOR_PRODUCAO.md)
