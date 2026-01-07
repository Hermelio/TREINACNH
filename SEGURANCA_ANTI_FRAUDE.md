# 🔒 Guia Completo de Segurança Anti-Fraude

## 📊 Sistema de Proteção em Camadas

### 1️⃣ Verificação de Identidade (Identity Verification)

#### ✅ Implementado:

**A. Verificação de Documentos com OCR**
- Upload de CNH com extração automática de dados
- Validação algorítmica de CNH e CPF
- Verificação de data de validade
- Confiança do OCR (0-100%)

**B. Verificação Facial (Face Matching)**
```python
# verification/validators.py
FraudPreventionValidator.validate_selfie_with_document()
```
- Compara selfie do instrutor com foto da CNH
- Usa reconhecimento facial (face-recognition library)
- Confiança mínima: 60%
- Previne: uso de documento de terceiros

#### 📋 Como Funciona:
```
1. Instrutor faz upload da CNH → OCR extrai dados
2. Instrutor envia selfie segurando o documento
3. Sistema compara rostos automaticamente
4. Admin revisa e aprova/rejeita
5. Perfil recebe selo de "Identidade Verificada" ✅
```

---

### 2️⃣ Verificação Multi-Etapas (Multi-Step Verification)

#### Campos no Profile:
```python
email_verified = BooleanField()      # Email confirmado
phone_verified = BooleanField()      # Telefone confirmado via SMS
identity_verified = BooleanField()   # Selfie + documento OK
```

#### Processo de Verificação:

**Etapa 1: Email** ✉️
- Link de confirmação enviado
- Token único com expiração
- Previne: emails falsos

**Etapa 2: Telefone** 📱
- SMS ou WhatsApp com código
- Validação contra VOIP/números temporários
- Previne: múltiplas contas com mesmo número

**Etapa 3: Identidade** 👤
- Upload de documento oficial
- Selfie com documento
- Comparação facial
- Previne: perfis falsos

**Etapa 4: Dados Bancários** 💳 (para instrutores)
- CPF do titular deve ser o mesmo do cadastro
- Previne: lavagem de dinheiro

---

### 3️⃣ Sistema de Confiança (Trust Score)

#### Cálculo do Score (0-100 pontos):

**Pontos Positivos (+):**
- ✅ Email verificado: **+10**
- ✅ Telefone verificado: **+10**
- ✅ Documento aprovado: **+15**
- ⭐ Cada avaliação positiva (≥4★): **+5** (max +15)
- 📅 Conta com +30 dias: **+5**

**Penalidades (-):**
- ❌ Cada documento rejeitado: **-10**
- 👎 Cada avaliação negativa (≤2★): **-10**
- 🚨 Denúncia confirmada: **-20**

#### Níveis de Confiança:
```
80-100: 🛡️ Altamente Confiável (verde)
60-79:  ✅ Confiável (azul)
40-59:  ⚠️ Moderado (amarelo)
0-39:   ❌ Baixa Confiança (vermelho)
```

#### Exibição no Perfil:
```django
{% load verification_tags %}
{% trust_score_badge user %}  {# Mostra badge colorido #}
```

---

### 4️⃣ Sistema de Denúncias (Reporting System)

#### Tipos de Denúncia:
- 🎭 **FAKE_PROFILE**: Perfil falso
- 📄 **FAKE_DOCUMENT**: Documento falsificado
- 💰 **SCAM**: Golpe financeiro
- 😠 **HARASSMENT**: Assédio
- 👻 **NO_SHOW**: Não compareceu
- ⭐ **POOR_SERVICE**: Serviço ruim

#### Fluxo de Denúncia:
```
1. Aluno/Instrutor faz denúncia
2. Anexa evidências (prints, fotos)
3. Admin investiga
4. Ações possíveis:
   - ⚠️ Advertência (warning)
   - ⏸️ Suspensão temporária
   - 🔴 Banimento permanente
```

#### Modelo:
```python
class UserReport(models.Model):
    reporter = ForeignKey(User)
    reported_user = ForeignKey(User)
    report_type = CharField(choices=ReportTypeChoices)
    description = TextField()
    evidence = FileField()  # Comprovante
    status = CharField()  # PENDING/INVESTIGATING/RESOLVED
    action_taken = CharField()  # NONE/WARNING/SUSPENSION/BAN
```

---

### 5️⃣ Blacklist de Documentos

#### Previne Reutilização:
```python
class DocumentBlacklist(models.Model):
    document_type = 'CNH' | 'CPF' | 'RG' | 'PHONE' | 'EMAIL'
    document_number = CharField()
    reason = 'FAKE' | 'STOLEN' | 'DUPLICATED' | 'FRAUD'
```

#### Validações Automáticas:
```python
# Antes de aprovar documento
FraudPreventionValidator.validate_cnh_not_blacklisted(cnh_number)

# Bloqueia automaticamente se estiver na lista
```

#### Casos de Uso:
- CNH falsificada detectada → blacklist permanente
- Mesmo CPF em múltiplas contas → bloqueio
- Telefone usado em golpe → blacklist

---

### 6️⃣ Detecção de Atividades Suspeitas

#### Sistema Automático:
```python
class SuspiciousActivity(models.Model):
    activity_type = CharField(choices=[
        'MULTIPLE_REJECTIONS',    # 3+ documentos rejeitados
        'RAPID_REGISTRATION',     # Cadastro muito rápido
        'FAKE_DATA',              # Dados inconsistentes
        'DUPLICATE_ACCOUNT',      # Mesmos dados em outra conta
        'ABNORMAL_BEHAVIOR',      # Padrão anormal
        'REPORTED_MULTIPLE'       # Múltiplas denúncias
    ])
    severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
```

#### Gatilhos Automáticos:

**🔴 CRITICAL (Crítico):**
- 5+ documentos rejeitados
- 3+ denúncias de golpe
- CPF/CNH na blacklist

**🟠 HIGH (Alto):**
- 3+ documentos rejeitados
- 2+ denúncias confirmadas
- Trust score < 20

**🟡 MEDIUM (Médio):**
- 2 documentos rejeitados
- 1 denúncia
- Dados duplicados

**🟢 LOW (Baixo):**
- Cadastro muito rápido
- Primeiro documento rejeitado

---

### 7️⃣ Validações Avançadas

#### A. Email Descartável
```python
FraudPreventionValidator.validate_email_domain(email)
```
Bloqueia: tempmail.com, guerrillamail.com, 10minutemail.com, etc.

#### B. Telefone VOIP
```python
FraudPreventionValidator.validate_phone_carrier(phone)
```
Valida se é número de operadora real (não VOIP)

#### C. Dados Duplicados
```python
FraudPreventionValidator.check_duplicate_data(cpf, phone, email)
```
Impede múltiplas contas com mesmos dados

#### D. Conta Bancária
```python
FraudPreventionValidator.validate_bank_account_ownership(cpf, bank_cpf)
```
Garante que conta bancária é do titular

---

### 8️⃣ Admin Dashboard de Segurança

#### Painel de Controle:

**📊 Denúncias Pendentes**
- Lista de reports não resolvidos
- Filtros por tipo e severidade
- Ações em massa

**🚨 Atividades Suspeitas**
- Alertas automáticos
- Ordem por severidade
- Marcar como revisado

**⚫ Blacklist de Documentos**
- Adicionar/remover documentos
- Histórico de bloqueios
- Expiração automática

**👥 Usuários Bloqueados**
- Lista de banimentos
- Motivo do bloqueio
- Opção de desbloquear

---

## 🛡️ Arquitetura de Segurança

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADAS DE PROTEÇÃO                       │
└─────────────────────────────────────────────────────────────┘

1️⃣ REGISTRO
   ├─ Email válido (não temporário) ✓
   ├─ Telefone real (não VOIP) ✓
   └─ CPF único ✓

2️⃣ VERIFICAÇÃO
   ├─ Confirmação de email ✓
   ├─ Confirmação de telefone (SMS) ✓
   ├─ Upload de CNH com OCR ✓
   ├─ Selfie com reconhecimento facial ✓
   └─ Comparação: selfie x CNH ✓

3️⃣ VALIDAÇÃO
   ├─ Algoritmo de validação CNH ✓
   ├─ Algoritmo de validação CPF ✓
   ├─ Data de validade do documento ✓
   ├─ Blacklist de documentos ✓
   └─ Dados não duplicados ✓

4️⃣ MONITORAMENTO
   ├─ Sistema de denúncias ✓
   ├─ Detecção automática de fraudes ✓
   ├─ Score de confiança dinâmico ✓
   └─ Logs de auditoria ✓

5️⃣ PUNIÇÕES
   ├─ Advertências
   ├─ Suspensão temporária
   ├─ Banimento permanente
   └─ Blacklist de documentos
```

---

## 🔧 Configuração e Uso

### Instalar Biblioteca de Reconhecimento Facial:
```bash
pip install face-recognition
```

### Habilitar Verificações:
```python
# settings.py
FRAUD_PREVENTION_ENABLED = True
FACE_MATCHING_REQUIRED = True  # Obriga selfie
MIN_TRUST_SCORE_TO_TEACH = 60  # Mínimo para dar aulas
```

### Template com Badges:
```django
{% load verification_tags %}

<div class="instructor-card">
    <h3>{{ instructor.user.get_full_name }}</h3>
    
    {# Badge de confiança #}
    {% trust_score_badge instructor.user %}
    
    {# Badges de verificação #}
    {% verification_badges instructor.user %}
    
    {# Alertas de segurança #}
    {% security_alerts instructor.user %}
    
    {# Progresso de verificação #}
    {% verification_progress instructor.user as progress %}
    <div class="progress">
        <div class="progress-bar" style="width: {{ progress }}%">
            {{ progress }}% verificado
        </div>
    </div>
</div>
```

---

## 📈 Métricas de Segurança

### Dashboard Recomendado:
- Total de usuários verificados vs não verificados
- Documentos aprovados/rejeitados/pendentes
- Denúncias por tipo
- Trust score médio da plataforma
- Usuários bloqueados por mês
- Tentativas de fraude detectadas

---

## ⚠️ Boas Práticas

### Para Segurança Máxima:

1. **Exija verificação completa antes de permitir aulas**
   ```python
   if not instructor.user.profile.identity_verified:
       return HttpResponse("Complete a verificação primeiro")
   ```

2. **Mostre badges visualmente nos perfis**
   - Usuários confiam mais em perfis verificados
   - Aumenta conversão de alunos

3. **Notifique sobre atividades suspeitas**
   ```python
   if suspicious_detected:
       send_admin_alert()
       send_user_email()
   ```

4. **Revise denúncias rapidamente**
   - Meta: resolver em 24h
   - Priorize denúncias de golpe/fraude

5. **Atualize trust score periodicamente**
   ```python
   # Task assíncrona (Celery)
   @periodic_task(run_every=crontab(hour=3, minute=0))
   def update_all_trust_scores():
       for user in User.objects.filter(profile__is_blocked=False):
           score = FraudPreventionValidator.calculate_trust_score(user)
           user.profile.trust_score = score
           user.profile.save()
   ```

---

## 🚀 Próximos Passos

### Melhorias Futuras:

- [ ] **Integração com Serpro** (validação oficial de CNH)
- [ ] **Machine Learning** para detectar padrões de fraude
- [ ] **Verificação em duas etapas** (2FA) com Google Authenticator
- [ ] **KYC completo** (Know Your Customer) para instrutores premium
- [ ] **Integração bancária** (validação de conta via PIX)
- [ ] **Background check** (antecedentes criminais)
- [ ] **Verificação de endereço** (conta de luz/água)
- [ ] **Sistema de reputação** com peso temporal (reviews recentes > antigas)
- [ ] **API de consulta de veículos** (verificar se instrutor tem carro)

---

## 📞 Contato e Suporte

Para dúvidas sobre segurança:
- Documentação: `SEGURANCA_ANTI_FRAUDE.md`
- Código: `verification/validators.py`
- Models: `verification/models_security.py`
- Admin: `verification/admin_security.py`

---

**Nota**: Este sistema multicamadas reduz drasticamente golpes, mas **nenhum sistema é 100% infalível**. Sempre mantenha revisão manual ativa e invista em educação dos usuários sobre segurança.
