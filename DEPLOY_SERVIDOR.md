# 🚀 Deploy do Sistema de Leads no Servidor

## Passo a Passo para Atualizar o Servidor

### 1. Conectar ao Servidor via SSH
```bash
ssh usuario@seu-servidor.com
# ou
ssh usuario@IP_DO_SERVIDOR
```

### 2. Navegar até o Diretório do Projeto
```bash
cd /caminho/para/TREINACNH
# Exemplo comum:
cd /var/www/treinacnh
# ou
cd ~/TREINACNH
```

### 3. Ativar o Ambiente Virtual
```bash
source venv/bin/activate
# ou se for outra pasta:
source env/bin/activate
```

### 4. Fazer Pull das Alterações
```bash
git pull origin main
```

### 5. Executar as Migrations
```bash
python manage.py migrate
```

### 6. Importar os Leads (IMPORTANTE!)
Antes de importar, certifique-se de que o arquivo `StudentLead.csv` está no servidor:

```bash
# Opção 1: Se você já tem o arquivo no servidor
python manage.py import_student_leads

# Opção 2: Se precisa enviar o arquivo do seu PC
# No seu PC (PowerShell):
scp StudentLead.csv usuario@servidor:/caminho/para/TREINACNH/

# Depois no servidor:
python manage.py import_student_leads
```

### 7. Coletar Arquivos Estáticos (se necessário)
```bash
python manage.py collectstatic --no-input
```

### 8. Reiniciar o Serviço

#### Para Gunicorn + Systemd:
```bash
sudo systemctl restart treinacnh
# ou
sudo systemctl restart gunicorn
```

#### Para Supervisor:
```bash
sudo supervisorctl restart treinacnh
```

#### Para Apache + mod_wsgi:
```bash
sudo systemctl restart apache2
```

#### Para Nginx + Gunicorn:
```bash
sudo systemctl restart treinacnh
sudo systemctl restart nginx
```

### 9. Verificar se Está Funcionando
```bash
# Ver logs em tempo real
tail -f /var/log/treinacnh/error.log
# ou
tail -f /var/log/nginx/error.log

# Verificar status do serviço
sudo systemctl status treinacnh
```

### 10. Testar no Admin
Acesse no navegador:
```
https://treinacnh.com.br/admin/marketplace/studentlead/
```

Você deve ver os 352 alunos importados!

---

## 🔍 Verificações Importantes

### Confirmar que os dados foram importados:
```bash
python manage.py shell
```

Dentro do shell Python:
```python
from marketplace.models import StudentLead
print(f"Total de alunos: {StudentLead.objects.count()}")
# Deve mostrar: Total de alunos: 352
```

### Verificar por estado:
```python
from django.db.models import Count
stats = StudentLead.objects.values('state__code').annotate(total=Count('id')).order_by('-total')
for s in stats[:5]:
    print(f"{s['state__code']}: {s['total']} alunos")
```

---

## ⚠️ Troubleshooting

### Erro: "No such file or directory: StudentLead.csv"
**Solução**: O arquivo CSV precisa estar na raiz do projeto. Use `scp` para enviá-lo:
```bash
# No seu PC:
scp StudentLead.csv usuario@servidor:/caminho/completo/para/TREINACNH/
```

### Erro: "relation marketplace_studentlead does not exist"
**Solução**: As migrations não foram aplicadas:
```bash
python manage.py migrate marketplace
```

### Erro: "State matching query does not exist"
**Solução**: Execute o comando novamente, ele cria os estados automaticamente:
```bash
python manage.py import_student_leads
```

### Serviço não reinicia
**Solução**: Verifique os logs:
```bash
sudo journalctl -u treinacnh -n 50 --no-pager
```

---

## 📝 Comandos Úteis Pós-Deploy

### Ver estatísticas rápidas:
```bash
python manage.py shell -c "
from marketplace.models import StudentLead
from django.db.models import Count
print('Total:', StudentLead.objects.count())
print('Por estado:', StudentLead.objects.values('state__code').annotate(c=Count('id')).order_by('-c')[:5])
"
```

### Backup do banco (antes de importar):
```bash
python manage.py dumpdata > backup_pre_leads.json
```

### Re-importar leads (se necessário):
```bash
# Apagar leads existentes
python manage.py shell -c "from marketplace.models import StudentLead; StudentLead.objects.all().delete()"

# Re-importar
python manage.py import_student_leads
```

---

## ✅ Checklist Final

- [ ] SSH no servidor
- [ ] Git pull origin main
- [ ] Ativar venv
- [ ] Executar migrations
- [ ] Enviar StudentLead.csv (se necessário)
- [ ] Importar leads: `python manage.py import_student_leads`
- [ ] Verificar: 352 alunos importados
- [ ] Collectstatic
- [ ] Reiniciar serviço
- [ ] Testar no admin
- [ ] Verificar mapa: estatísticas aparecendo
- [ ] Testar notificações (cadastrar instrutor teste)

---

## 🎯 Próximas Ações (Após Deploy)

1. **Acessar Admin**: `/admin/marketplace/studentlead/`
2. **Filtrar por estado**: Ver quais estados têm mais demanda
3. **Identificar oportunidades**: Estados com alunos mas sem instrutores
4. **Começar notificações**: Usar botões do WhatsApp para contatar alunos
5. **Campanhas de marketing**: Focar nos estados com mais demanda

---

## 📞 Em Caso de Problemas

Se algo der errado, você pode reverter:
```bash
git revert HEAD
python manage.py migrate marketplace zero
python manage.py migrate
sudo systemctl restart treinacnh
```

---

**Data do Deploy**: _________________  
**Responsável**: _________________  
**Status**: [ ] Sucesso  [ ] Problemas (detalhar):
