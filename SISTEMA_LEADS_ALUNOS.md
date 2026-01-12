# Sistema de Leads de Alunos - TREINACNH

## 📋 Visão Geral

Sistema implementado para transformar o projeto TREINACNH e atrair mais instrutores, mostrando a demanda real de alunos aguardando instrutores em cada estado do Brasil.

## ✅ O que foi implementado

### 1. **Modelo StudentLead**
- Novo modelo no `marketplace/models.py` para armazenar leads de alunos
- Campos principais:
  - Nome, telefone, email, cidade, estado
  - Categoria CNH desejada (A, B, AB, C, D, E)
  - Status de teoria (já possui ou não)
  - Preferências de marketing/WhatsApp
  - Status de contato e notificação

### 2. **Importação de Dados**
- **352 alunos** importados com sucesso do arquivo `StudentLead.csv`
- Management command: `python manage.py import_student_leads`
- Suporta modo dry-run: `python manage.py import_student_leads --dry-run`

### 3. **Mapa Atualizado**
O mapa em `marketplace/views_map.py` agora mostra:
- **Instrutores cadastrados** (marcadores no mapa)
- **Estatísticas de alunos por estado**:
  - Total de alunos cadastrados
  - Alunos aguardando notificação
  - Estados sem instrutores disponíveis

### 4. **Sistema de Notificação Automática**
Signal em `marketplace/signals.py` que:
- Detecta quando um novo instrutor é **verificado** em um estado
- Marca automaticamente todos os alunos daquele estado como "notificados"
- Logs automáticos para acompanhamento

### 5. **Admin Completo**
Interface administrativa em `marketplace/admin.py` com:

#### Funcionalidades para StudentLead:
- **Visualização completa** de todos os alunos
- **Filtros por**: Estado, Categoria, Status de contato
- **Indicador visual**: Mostra se há instrutor disponível no estado
- **Link direto WhatsApp**: Botão para enviar mensagem automaticamente
- **Ações em massa**:
  - Marcar como notificado sobre instrutores
  - Marcar como contatado
  - Exportar telefones para contato em massa

## 📊 Distribuição de Alunos por Estado

Após a importação, os 352 alunos estão distribuídos por estado. Principais concentrações:
- **SP (São Paulo)**: Maior concentração
- **RJ (Rio de Janeiro)**: Segunda maior
- **MG, PR, RS, SC**: Concentrações relevantes
- Presença em todos os estados brasileiros

## 🚀 Como Usar

### Para Administradores:

1. **Acessar leads no admin**:
   ```
   /admin/marketplace/studentlead/
   ```

2. **Ver alunos aguardando em um estado**:
   - Filtrar por estado
   - Filtrar por "Notificado sobre instrutor = Não"

3. **Entrar em contato via WhatsApp**:
   - Clicar no botão "📱 Enviar WhatsApp" na página de detalhes
   - Mensagem pré-formatada será aberta

4. **Notificar alunos quando houver instrutor**:
   - Selecionar alunos do estado
   - Ação: "Marcar como notificado sobre instrutores"
   - Usar links do WhatsApp para enviar mensagens

### Para Instrutores (novos cadastros):

Quando um instrutor se cadastra e é verificado:
1. O sistema **automaticamente marca** todos os alunos do estado
2. Admin recebe **log informando** quantos alunos foram marcados
3. Admin pode **filtrar e contatar** esses alunos

## 📱 Mensagens Sugeridas para WhatsApp

### Para alunos quando instrutor se cadastra:
```
Olá [Nome]! Boas notícias! 

Agora temos instrutores verificados disponíveis em [Estado]. 

Confira os instrutores disponíveis em:
https://treinacnh.com.br/mapa

Estamos aqui para ajudar você a tirar sua CNH!
```

### Para atrair instrutores:
```
[Nome], veja quantos alunos estão aguardando instrutores em [Estado]!

🎯 [X] alunos cadastrados no seu estado
📍 Veja o mapa completo: https://treinacnh.com.br/mapa

Cadastre-se como instrutor e comece a dar aulas hoje!
```

## 🔄 Workflow de Notificação

```
1. Instrutor se cadastra → 2. Admin verifica instrutor → 
3. Signal automático marca alunos → 4. Admin filtra alunos marcados → 
5. Admin envia WhatsApp via botão → 6. Aluno conhece instrutor
```

## 📈 Próximos Passos Sugeridos

1. **Integração com API do WhatsApp**
   - Automatizar envio de mensagens
   - Usar WhatsApp Business API

2. **Dashboard de Conversão**
   - Quantos alunos foram notificados
   - Quantos entraram em contato com instrutores
   - Taxa de conversão por estado

3. **Sistema de Matching Automático**
   - Sugerir instrutores próximos automaticamente
   - Email automático para alunos

4. **Geolocalização dos Alunos**
   - Adicionar coordenadas aos leads
   - Mostrar densidade de alunos no mapa
   - Heatmap de demanda

## 🗂️ Arquivos Modificados/Criados

### Modelos:
- `marketplace/models.py` - Adicionado modelo `StudentLead`

### Views:
- `marketplace/views_map.py` - Atualizado para mostrar estatísticas de alunos

### Admin:
- `marketplace/admin.py` - Adicionado admin completo para `StudentLead`

### Management Commands:
- `marketplace/management/commands/import_student_leads.py` - Comando de importação

### Signals:
- `marketplace/signals.py` - Criado sistema de notificação automática
- `marketplace/apps.py` - Configurado para carregar signals

### Migrations:
- `marketplace/migrations/0004_studentlead.py` - Migration do novo modelo

## 💡 Dicas de Uso

### Encontrar estados com mais demanda:
```python
# No Django shell
from marketplace.models import StudentLead
from django.db.models import Count

StudentLead.objects.values('state__code', 'state__name')\
    .annotate(total=Count('id'))\
    .order_by('-total')
```

### Alunos aguardando sem instrutor:
```python
StudentLead.objects.filter(
    notified_about_instructor=False
).values('state__code').annotate(total=Count('id'))
```

### Listar telefones para contato em massa (estado específico):
```python
leads = StudentLead.objects.filter(
    state__code='SP',
    accept_whatsapp=True
)
phones = [lead.phone for lead in leads]
```

## 🎯 Métricas para Acompanhar

1. **Total de alunos cadastrados**: 352
2. **Alunos por estado** (varia)
3. **Alunos notificados vs aguardando**
4. **Taxa de resposta dos alunos**
5. **Conversões (alunos → contratos)**

## ⚠️ Observações Importantes

- Os dados do CSV foram importados preservando IDs externos
- Telefones no formato brasileiro (podem ter DDD)
- Emails podem estar vazios em alguns registros
- Sistema respeita preferências de WhatsApp/Marketing
- Notificações são marcadas mas envio é manual (por enquanto)

## 🔐 Segurança e Privacidade

- Dados pessoais armazenados com segurança
- Respeito às preferências de contato dos alunos
- Apenas admins autorizados podem ver leads
- LGPD: Sistema permite exclusão de dados mediante solicitação

---

**Status**: ✅ Sistema implementado e funcionando
**Data**: Janeiro 2026
**Versão**: 1.0
