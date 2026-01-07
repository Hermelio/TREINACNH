# TREINACNH - Marketplace de Instrutores de Direção

Plataforma web para conectar alunos e instrutores de direção, com sistema de verificação de documentos, avaliações, leads e gestão de planos.

## � Documentação Completa

- **[SERVIDOR_PRODUCAO.md](SERVIDOR_PRODUCAO.md)** - 🔥 Configurações completas do servidor de produção
- **[CONFIGURACAO_LOGO.md](CONFIGURACAO_LOGO.md)** - Logo e identidade visual
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Visão geral do projeto
- **[SETUP_WINDOWS.md](SETUP_WINDOWS.md)** - Instalação no Windows
- **[VERIFICACAO_DOCUMENTOS.md](VERIFICACAO_DOCUMENTOS.md)** - Sistema de verificação
- **[SEGURANCA_ANTI_FRAUDE.md](SEGURANCA_ANTI_FRAUDE.md)** - Segurança

## 🌐 Site em Produção

- **URL**: http://72.61.36.89:8080/
- **Status**: ✅ Online e funcionando

## �🚀 Características Principais

- **Marketplace completo**: Busca por cidade/UF, filtros avançados, perfis detalhados
- **Verificação de documentos**: Sistema de upload e aprovação de CNH, certificados
- **Avaliações e denúncias**: Moderação de reviews e reports
- **Contato direto**: Integração com WhatsApp para comunicação
- **Gestão de leads**: Controle de solicitações de contato
- **Sistema de planos**: Assinaturas e destaques (sem pagamento real)
- **Admin completo**: Painel de moderação, analytics e auditoria
- **Design responsivo**: Bootstrap 5 + templates otimizados

## 📋 Requisitos

- Python 3.11+
- MySQL 5.7+ (configurado com as credenciais fornecidas)
- Linux (recomendado para produção) ou Windows (desenvolvimento)

## 🛠️ Setup - Ambiente de Desenvolvimento

### 1. Clone/Baixe o Projeto

```bash
cd c:\Users\Windows\OneDrive\Documentos\PROJETOS\TREINACNH
```

### 2. Crie o Ambiente Virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instale as Dependências

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```powershell
Copy-Item .env.example .env
```

Edite o arquivo `.env` e ajuste conforme necessário (já vem com as credenciais do MySQL configuradas):

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (MySQL)
DB_HOST=10.54.4.7
DB_PORT=3306
DB_NAME=Raio_X
DB_USER=integrador
DB_PASSWORD=crystalcomgas
```

**⚠️ IMPORTANTE:** Em produção, gere uma SECRET_KEY segura:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Crie as Tabelas no Banco de Dados

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie o Superusuário (Admin)

```powershell
python manage.py createsuperuser
```

Preencha as informações solicitadas.

### 7. Popule Dados Iniciais (Opcional)

Crie alguns dados de teste via Django shell:

```powershell
python manage.py shell
```

```python
from marketplace.models import State, City, CategoryCNH

# Estados
sp = State.objects.create(code='SP', name='São Paulo')
rj = State.objects.create(code='RJ', name='Rio de Janeiro')
mg = State.objects.create(code='MG', name='Minas Gerais')

# Cidades
City.objects.create(state=sp, name='São Paulo', is_active=True)
City.objects.create(state=sp, name='Campinas', is_active=True)
City.objects.create(state=rj, name='Rio de Janeiro', is_active=True)
City.objects.create(state=mg, name='Belo Horizonte', is_active=True)

# Categorias CNH
CategoryCNH.objects.create(code='A', label='Categoria A - Motos')
CategoryCNH.objects.create(code='B', label='Categoria B - Carros')
CategoryCNH.objects.create(code='C', label='Categoria C - Caminhões')
CategoryCNH.objects.create(code='D', label='Categoria D - Ônibus')
CategoryCNH.objects.create(code='E', label='Categoria E - Carretas')

exit()
```

### 8. Crie Diretórios para Logs e Media

```powershell
New-Item -ItemType Directory -Force -Path logs
New-Item -ItemType Directory -Force -Path media
New-Item -ItemType Directory -Force -Path static
```

### 9. Execute o Servidor de Desenvolvimento

```powershell
python manage.py runserver
```

Acesse: [http://localhost:8000](http://localhost:8000)

Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

## 📦 Estrutura do Projeto

```
TREINACNH/
├── accounts/           # Autenticação e perfis de usuários
├── marketplace/        # Cidades, instrutores, leads
├── verification/       # Upload e verificação de documentos
├── reviews/           # Avaliações e denúncias
├── billing/           # Planos e destaques
├── core/              # Páginas públicas, FAQ, home
├── config/            # Configurações Django
├── templates/         # Templates HTML Bootstrap 5
├── static/            # CSS, JS, imagens (arquivos estáticos)
├── media/             # Uploads de usuários
├── logs/              # Logs da aplicação
├── manage.py
├── requirements.txt
└── README.md
```

## 🎯 Funcionalidades por App

### **accounts**
- Registro de usuários (aluno/instrutor)
- Login/logout
- Edição de perfil
- Dashboard personalizado por role

### **marketplace**
- Listagem de cidades por UF
- Busca e filtros de instrutores
- Perfil público do instrutor
- Sistema de leads (solicitação de contato)
- Gestão de perfil profissional

### **verification**
- Upload de documentos (CNH, certificados)
- Fila de revisão no admin
- Aprovação/rejeição com notas
- Auditoria de ações

### **reviews**
- Avaliações (1-5 estrelas)
- Comentários moderados
- Sistema de denúncias
- Investigação de reports

### **billing**
- Planos para instrutores
- Assinaturas (controle manual)
- Destaques em cidades
- Gestão de períodos

### **core**
- Homepage com busca
- Páginas institucionais (Sobre, FAQ, Contato)
- Termos e privacidade
- Healthcheck endpoint

## 🔒 Segurança

O projeto implementa:

- ✅ CSRF protection (Django padrão)
- ✅ Validação server-side em todos os forms
- ✅ Sanitização de inputs
- ✅ Headers de segurança (produção)
- ✅ Upload seguro de arquivos (tamanho, tipo)
- ✅ Auditoria de ações do admin
- ✅ Logs estruturados
- ✅ Rate limiting básico (django-ratelimit)

### Checklist de Hardening para Produção

Antes de fazer deploy, verifique:

1. **Variáveis de Ambiente**
   ```env
   DEBUG=False
   SECRET_KEY=<chave-forte-gerada>
   ALLOWED_HOSTS=seudominio.com,www.seudominio.com
   ```

2. **Headers de Segurança**
   ```env
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_HSTS_SECONDS=31536000
   ```

3. **Arquivos Estáticos**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Permissões de Arquivos**
   ```bash
   chmod 750 /path/to/project
   chmod 640 /path/to/project/.env
   ```

5. **Database Backup**
   Configure backups automáticos do MySQL

## 🚀 Deploy em Produção (Linux)

### Opção 1: Gunicorn + Nginx (Recomendado)

#### 1. Instale Dependências no Servidor

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nginx mysql-client
```

#### 2. Configure o Projeto

```bash
cd /var/www/treinacnh
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Configure o `.env` de Produção

```bash
nano .env
```

```env
DEBUG=False
SECRET_KEY=<sua-secret-key-forte>
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

DB_HOST=10.54.4.7
DB_PORT=3306
DB_NAME=Raio_X
DB_USER=integrador
DB_PASSWORD=crystalcomgas

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

#### 4. Execute Migrações e Collect Static

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 5. Crie Serviço Systemd

```bash
sudo nano /etc/systemd/system/treinacnh.service
```

```ini
[Unit]
Description=TREINACNH Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/treinacnh
Environment="PATH=/var/www/treinacnh/venv/bin"
ExecStart=/var/www/treinacnh/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/treinacnh/gunicorn.sock \
          --timeout 120 \
          --access-logfile /var/www/treinacnh/logs/access.log \
          --error-logfile /var/www/treinacnh/logs/error.log \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 6. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/treinacnh
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/treinacnh/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/treinacnh/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://unix:/var/www/treinacnh/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/treinacnh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Inicie o Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl start treinacnh
sudo systemctl enable treinacnh
sudo systemctl status treinacnh
```

#### 8. SSL com Let's Encrypt (Opcional mas Recomendado)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

## 📊 Admin - Funcionalidades Extras

### Analytics Simples

No Django Admin, você pode criar queries customizadas. Exemplo de view para analytics:

```python
# Em core/admin.py ou criar um arquivo analytics.py

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count
from marketplace.models import InstructorProfile, Lead, City

@staff_member_required
def analytics_view(request):
    stats = {
        'total_instructors': InstructorProfile.objects.count(),
        'verified_instructors': InstructorProfile.objects.filter(is_verified=True).count(),
        'total_leads': Lead.objects.count(),
        'leads_by_city': Lead.objects.values('city__name').annotate(count=Count('id')).order_by('-count')[:10],
        'top_cities': City.objects.annotate(
            instructor_count=Count('instructors', filter=Q(instructors__is_visible=True))
        ).order_by('-instructor_count')[:10],
    }
    return render(request, 'admin/analytics.html', {'stats': stats})
```

## 🧪 Testes

Execute os testes:

```bash
python manage.py test
```

Para testes com coverage:

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Gera relatório HTML em htmlcov/
```

## 📝 Comandos Úteis

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Shell interativo
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic

# Ver todas as URLs
python manage.py show_urls  # Requer django-extensions

# Limpar sessões expiradas
python manage.py clearsessions

# Verificar problemas no projeto
python manage.py check

# Backup do banco (MySQL)
mysqldump -h 10.54.4.7 -u integrador -p Raio_X > backup_$(date +%Y%m%d).sql
```

## 🔧 Troubleshooting

### Erro de conexão com MySQL

```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server...")
```

**Solução:**
- Verifique se o MySQL está rodando: `systemctl status mysql`
- Teste conexão: `mysql -h 10.54.4.7 -u integrador -p Raio_X`
- Verifique firewall: `sudo ufw allow from SEU_IP to any port 3306`

### Erro de permissão em media/

```
PermissionError: [Errno 13] Permission denied: '/path/to/media/'
```

**Solução:**
```bash
sudo chown -R www-data:www-data /var/www/treinacnh/media
sudo chmod -R 755 /var/www/treinacnh/media
```

### Arquivos estáticos não carregam

**Solução:**
```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx
```

## 📚 Documentação Adicional

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

## 🤝 Suporte

Para dúvidas ou problemas:
1. Verifique os logs: `tail -f logs/django.log`
2. Verifique logs do Gunicorn: `/var/www/treinacnh/logs/error.log`
3. Verifique logs do Nginx: `sudo tail -f /var/log/nginx/error.log`

## 📄 Licença

Este projeto é proprietário e confidencial. Todos os direitos reservados.

## 🎉 Pronto!

Seu marketplace de instrutores está configurado e pronto para uso!

**Endpoints principais:**
- Home: [http://localhost:8000/](http://localhost:8000/)
- Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Cidades: [http://localhost:8000/instrutores/cidades/](http://localhost:8000/instrutores/cidades/)
- Healthcheck: [http://localhost:8000/healthcheck/](http://localhost:8000/healthcheck/)

---

**Desenvolvido com ❤️ usando Django + Bootstrap 5**
