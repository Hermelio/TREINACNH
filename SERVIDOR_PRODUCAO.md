# Configuração do Servidor de Produção - TREINACNH

## 📋 Informações do Servidor

- **IP**: 72.61.36.89
- **Usuário**: root
- **Senha**: Leds@131610@234645?
- **Porta SSH**: 22
- **Porta HTTP**: 8080

## 🔑 Acesso SSH Configurado

Chave SSH configurada em: `C:\Users\Windows\.ssh\id_rsa`
- Acesso sem senha ativado
- Comando: `ssh root@72.61.36.89`

## 🗄️ Banco de Dados MySQL

### Credenciais
- **Host**: localhost
- **Porta**: 3306
- **Database**: treinacnh
- **Usuário**: integrador
- **Senha**: `Crystal@comgas2024!`

### Comandos Úteis
```bash
# Acessar MySQL
mysql -u integrador -p'Crystal@comgas2024!' treinacnh

# Backup do banco
mysqldump -u integrador -p'Crystal@comgas2024!' treinacnh > backup.sql

# Restaurar backup
mysql -u integrador -p'Crystal@comgas2024!' treinacnh < backup.sql
```

## 📁 Estrutura do Servidor

```
/var/www/TREINACNH/
├── .env                    # Variáveis de ambiente
├── manage.py              # Django management
├── venv/                  # Ambiente virtual Python
├── static/                # Arquivos estáticos
│   └── images/
│       └── logo.png       # Logo do site (52KB)
├── staticfiles/           # Arquivos coletados (collectstatic)
├── media/                 # Uploads de usuários
├── logs/                  # Logs do sistema
│   ├── django.log
│   ├── gunicorn-access.log
│   └── gunicorn-error.log
└── config/                # Configurações Django
    └── settings.py
```

## ⚙️ Arquivo .env no Servidor

```bash
SECRET_KEY=blof=5nb48cmev0bnlqis(or^t29=xd@sd^8-iohbqgwcw79ah
DEBUG=False
ALLOWED_HOSTS=72.61.36.89,localhost,127.0.0.1
DATABASE_URL=postgres://treinacnh_user:TreinaCNH@2026@localhost:5432/treinacnh
SECURE_SSL_REDIRECT=False

# Configurações MySQL (Ativas)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=treinacnh
DB_USER=integrador
DB_PASSWORD=Crystal@comgas2024!

# Configurações do Site
SITE_NAME=TREINACNH
SITE_LOGO=images/logo.png
SITE_URL=http://72.61.36.89:8080
```

## 🚀 Serviços Systemd

### Gunicorn
```bash
# Status
systemctl status gunicorn-treinacnh

# Reiniciar
systemctl restart gunicorn-treinacnh

# Logs
journalctl -u gunicorn-treinacnh -f

# Configuração
/etc/systemd/system/gunicorn-treinacnh.service
```

### Nginx
```bash
# Status
systemctl status nginx

# Reiniciar
systemctl restart nginx

# Configuração
/etc/nginx/sites-enabled/treinacnh

# Logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

## 🔄 Comandos de Deploy

### Atualizar Código
```bash
ssh root@72.61.36.89 'cd /var/www/TREINACNH && git pull origin main'
```

### Coletar Arquivos Estáticos
```bash
ssh root@72.61.36.89 'cd /var/www/TREINACNH && source venv/bin/activate && python manage.py collectstatic --noinput'
```

### Executar Migrações
```bash
ssh root@72.61.36.89 'cd /var/www/TREINACNH && source venv/bin/activate && python manage.py migrate'
```

### Reiniciar Serviços
```bash
ssh root@72.61.36.89 'systemctl restart gunicorn-treinacnh && systemctl restart nginx'
```

### Deploy Completo (Um comando)
```bash
ssh root@72.61.36.89 'cd /var/www/TREINACNH && git pull origin main && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && systemctl restart gunicorn-treinacnh'
```

## 📝 Comandos Django Úteis

```bash
# Conectar ao servidor e ativar ambiente
ssh root@72.61.36.89
cd /var/www/TREINACNH
source venv/bin/activate

# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Verificar configurações
python manage.py check

# Ver migrações pendentes
python manage.py showmigrations
```

## 🎨 Logo do Site

- **Localização Local**: `static/images/logo.png` (52KB)
- **Localização Servidor**: `/var/www/TREINACNH/static/images/logo.png`
- **URL Original**: https://TreinaCNH.com.br/logo.png
- **Configuração**: Automaticamente exibida no navbar e footer

## 🔧 Troubleshooting

### Site não carrega (504 Gateway Timeout)
```bash
# Verificar gunicorn
systemctl status gunicorn-treinacnh
journalctl -u gunicorn-treinacnh -n 50

# Testar conexão local
curl -I http://127.0.0.1:8001/
```

### Erro de banco de dados
```bash
# Verificar credenciais
cat /var/www/TREINACNH/.env | grep DB_

# Testar conexão MySQL
mysql -u integrador -p'Crystal@comgas2024!' treinacnh -e "SELECT 1;"
```

### Arquivos estáticos não carregam
```bash
# Coletar novamente
python manage.py collectstatic --noinput

# Verificar permissões
ls -la /var/www/TREINACNH/staticfiles/
```

### Logo não aparece
```bash
# Verificar arquivo
ls -lh /var/www/TREINACNH/static/images/logo.png

# Baixar novamente
cd /var/www/TREINACNH/static/images/
wget https://TreinaCNH.com.br/logo.png -O logo.png

# Coletar estáticos
python manage.py collectstatic --noinput
```

## 📊 Monitoramento

### Ver logs em tempo real
```bash
# Django
tail -f /var/www/TREINACNH/logs/django.log

# Gunicorn Access
tail -f /var/www/TREINACNH/logs/gunicorn-access.log

# Gunicorn Error
tail -f /var/www/TREINACNH/logs/gunicorn-error.log

# Nginx Error
tail -f /var/log/nginx/error.log
```

### Verificar processos
```bash
# Ver processos Python/Gunicorn
ps aux | grep gunicorn

# Uso de memória
free -h

# Espaço em disco
df -h
```

## 🔐 Segurança

### Backup Recomendado
```bash
# Backup completo
ssh root@72.61.36.89 'cd /var/www && tar -czf treinacnh_backup_$(date +%Y%m%d).tar.gz TREINACNH/'

# Backup apenas banco
ssh root@72.61.36.89 'mysqldump -u integrador -p"Crystal@comgas2024!" treinacnh > /tmp/treinacnh_db_$(date +%Y%m%d).sql'

# Download do backup
scp root@72.61.36.89:/tmp/treinacnh_db_*.sql ./backups/
```

### Firewall
- Porta 22 (SSH): Aberta
- Porta 8080 (HTTP): Aberta
- Porta 3306 (MySQL): Local apenas

## 📌 URLs Importantes

- **Site**: http://72.61.36.89:8080/
- **Admin**: http://72.61.36.89:8080/admin/
- **API**: http://72.61.36.89:8080/api/

## 📅 Histórico de Alterações

### 07/01/2026
- ✅ Configuração inicial do servidor
- ✅ Banco MySQL criado (treinacnh)
- ✅ Usuário MySQL: integrador com senha forte
- ✅ Logo configurada e baixada
- ✅ Context processor criado para logo
- ✅ Migrações executadas com sucesso
- ✅ Site rodando em http://72.61.36.89:8080/
- ✅ Acesso SSH sem senha configurado

## 🎯 Próximos Passos

1. [ ] Criar superusuário Django
2. [ ] Configurar domínio (treinacnh.com.br)
3. [ ] Configurar SSL/HTTPS
4. [ ] Configurar backup automático
5. [ ] Configurar monitoramento
6. [ ] Otimizar configurações de produção

---

**Última atualização**: 07/01/2026 22:30 UTC
**Status**: ✅ Produção - Funcionando
