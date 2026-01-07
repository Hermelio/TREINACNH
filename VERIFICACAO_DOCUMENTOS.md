# Sistema de Verificação de Documentos

## 📋 Visão Geral

O sistema de verificação foi desenvolvido para validar documentos de instrutores, especialmente CNH (Carteira Nacional de Habilitação), utilizando:

1. **OCR (Reconhecimento Óptico de Caracteres)** - Extração automática de dados
2. **Validação Algorítmica** - Verificação de CPF e CNH
3. **Revisão Manual** - Aprovação final pelo administrador

## ⚠️ Importante sobre API do DETRAN

**NÃO EXISTE API PÚBLICA DO DETRAN** para validação de CNH. As opções são:

### Soluções Implementadas:

✅ **OCR com pytesseract**: Extrai dados automaticamente da foto da CNH
✅ **Validação de dígitos**: Algoritmo que verifica se o número da CNH é válido
✅ **Validação de CPF**: Calcula dígitos verificadores do CPF
✅ **Verificação de validade**: Checa se o documento está dentro da validade
✅ **Revisão manual**: Admin revisa e aprova/rejeita documentos

### Soluções Futuras (Pagas):

🔐 **API Serpro** (https://www.serpro.gov.br/)
- API oficial do governo federal
- Acesso a base de dados do DETRAN
- **Requer autorização governamental**
- **É pago** (cobrança por consulta)
- Preparado no código via `prepare_serpro_integration_data()`

## 🔧 Como Funciona

### 1. Upload do Documento

O instrutor faz upload da CNH (foto ou scan) através da página de documentos.

```python
# verification/views.py
document = InstructorDocument.objects.create(
    instructor=instructor_profile,
    doc_type='CNH',
    file=uploaded_file
)
```

### 2. Processamento OCR Automático

O sistema usa `pytesseract` para extrair texto da imagem:

```python
from .services import DocumentVerificationService

service = DocumentVerificationService()
ocr_data = service.extract_cnh_data(document.file.path)

# Dados extraídos:
# - cnh_number: Número da CNH (11 dígitos)
# - cpf: CPF do titular
# - name: Nome completo
# - validity_date: Data de validade
# - confidence: Confiança da extração (0-100%)
```

### 3. Validação Algorítmica

O sistema valida os dados extraídos:

**Validação de CNH:**
```python
cnh_valid = service.validate_cnh_number('12345678901')
# Verifica o dígito verificador usando algoritmo oficial
```

**Validação de CPF:**
```python
cpf_valid = service.validate_cpf('12345678901')
# Calcula os 2 dígitos verificadores
```

**Verificação de Validade:**
```python
validity_ok = service.check_cnh_validity(validity_date)
# Compara com a data atual
```

### 4. Armazenamento dos Resultados

Todos os dados são salvos no modelo `InstructorDocument`:

```python
document.extracted_cnh_number = '12345678901'
document.extracted_cpf = '98765432100'
document.extracted_name = 'João da Silva'
document.extracted_validity = date(2025, 12, 31)
document.ocr_confidence = 85.5

document.cnh_valid = True  # ✅ CNH válida
document.cpf_valid = True  # ✅ CPF válido
document.validity_ok = True  # ✅ Dentro da validade

document.save()
```

### 5. Revisão Manual no Admin

O administrador acessa `/admin/verification/instructordocument/` e vê:

- 📄 Documento original (preview)
- 🤖 Dados extraídos via OCR
- ✅ Resultados das validações automáticas
- 📝 Campo para observações
- 🔘 Botões: Aprovar / Rejeitar

## 📦 Modelos de Dados

### InstructorDocument

```python
class InstructorDocument(models.Model):
    # Documento
    instructor = ForeignKey(InstructorProfile)
    doc_type = CharField(choices=['CNH', 'CERT_INSTRUTOR', ...])
    file = FileField(upload_to='documents/%Y/%m/')
    
    # Dados extraídos via OCR
    extracted_cnh_number = CharField(max_length=11)
    extracted_cpf = CharField(max_length=11)
    extracted_name = CharField(max_length=200)
    extracted_validity = DateField()
    ocr_confidence = DecimalField(max_digits=5, decimal_places=2)
    
    # Resultados da validação
    cnh_valid = BooleanField()  # Número da CNH é válido?
    cpf_valid = BooleanField()  # CPF é válido?
    validity_ok = BooleanField()  # Está dentro da validade?
    
    # Revisão manual
    status = CharField(choices=['PENDING', 'APPROVED', 'REJECTED'])
    notes = TextField()  # Observações do revisor
    reviewed_by = ForeignKey(User)
    reviewed_at = DateTimeField()
```

### Profile (accounts/models.py)

Adicionado campos para validação:

```python
class Profile(models.Model):
    cpf = CharField(max_length=11, unique=True)
    birth_date = DateField()
```

## 🚀 Configuração

### 1. Instalar Tesseract OCR

O pytesseract precisa do executável Tesseract instalado:

**Windows:**
1. Baixe o instalador: https://github.com/UB-Mannheim/tesseract/wiki
2. Instale (padrão: `C:\Program Files\Tesseract-OCR`)
3. Configure o caminho no código:

```python
# verification/services.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-por

# Mac
brew install tesseract tesseract-lang
```

### 2. Pacotes Python

Já instalados:
```bash
pip install pytesseract opencv-python Pillow
```

## 📖 Como Usar

### Para Instrutores:

1. Acesse "Meus Documentos" no menu
2. Clique em "Enviar Documento"
3. Selecione o tipo (CNH, Certificado, etc.)
4. Faça upload da foto/scan
5. Aguarde o processamento OCR (instantâneo)
6. Veja o feedback com validações
7. Aguarde aprovação do admin

### Para Administradores:

1. Acesse `/admin/verification/instructordocument/`
2. Filtre por status "Pendente"
3. Clique no documento para revisar
4. Veja os dados extraídos automaticamente
5. Compare com o arquivo original
6. Aprove ou rejeite com observações

## 🎯 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INSTRUTOR FAZ UPLOAD DA CNH                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SISTEMA PROCESSA COM OCR                                 │
│    ├─ Extrai: CNH, CPF, Nome, Validade                      │
│    ├─ Valida: Algoritmo CNH, Algoritmo CPF                  │
│    └─ Verifica: Data de validade                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. RESULTADOS SALVOS NO BANCO                               │
│    Status: PENDING (Pendente)                               │
│    ✅ CNH válida | ✅ CPF válido | ✅ Dentro da validade    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. ADMIN REVISA MANUALMENTE                                 │
│    ├─ Compara dados extraídos com foto                      │
│    ├─ Verifica se foto é autêntica                          │
│    └─ Aprova ou rejeita                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. STATUS ATUALIZADO                                        │
│    Status: APPROVED ✅ ou REJECTED ❌                       │
│    Instrutor recebe notificação                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Segurança e LGPD

- ✅ Documentos armazenados em `media/documents/` (privado)
- ✅ Acesso restrito: apenas dono do documento e admins
- ✅ Dados sensíveis (CPF) criptografados no banco (recomendado)
- ✅ Log de auditoria em `AuditLog`
- ✅ Política de retenção: documentos aprovados mantidos por X anos

## 🔧 Melhorias Futuras

- [ ] Integração com API Serpro (quando contratada)
- [ ] Machine Learning para detectar CNH falsificada
- [ ] Upload via câmera do celular (Progressive Web App)
- [ ] Notificações push quando documento for aprovado
- [ ] Dashboard com estatísticas de aprovação
- [ ] Renovação automática quando CNH estiver próxima do vencimento

## 📞 Suporte

Para dúvidas sobre validação de documentos, consulte:
- Código: `verification/services.py`
- Documentação Serpro: https://www.serpro.gov.br/
- LGPD: https://www.gov.br/lgpd/

---

**Nota**: O OCR não é 100% preciso. A revisão manual pelo administrador é **essencial** para garantir autenticidade dos documentos.
