# ⚠️ Python não encontrado! Guia de Instalação Windows

## 📥 Passo 1: Instalar Python 3.11+

### Opção A: Via Site Oficial (Recomendado)
1. Acesse: https://www.python.org/downloads/
2. Baixe **Python 3.11** ou superior
3. **IMPORTANTE:** Durante a instalação, marque:
   - ✅ **"Add Python to PATH"** (essencial!)
   - ✅ "Install for all users" (opcional)
4. Clique em "Install Now"
5. Reinicie o terminal após a instalação

### Opção B: Via Winget (Windows 11)
```powershell
winget install Python.Python.3.11
```

### Opção C: Via Chocolatey
```powershell
choco install python311
```

## ✅ Verificar Instalação

Após instalar, **FECHE e REABRA o terminal PowerShell**, depois execute:

```powershell
python --version
# Deve mostrar: Python 3.11.x ou superior
```

## 🚀 Executar o Projeto (Após Instalar Python)

### 1. Criar Ambiente Virtual
```powershell
cd C:\Users\Windows\OneDrive\Documentos\PROJETOS\TREINACNH
python -m venv venv
```

### 2. Ativar Ambiente Virtual
```powershell
.\venv\Scripts\Activate.ps1
```

**Se der erro de política de execução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```powershell
Copy-Item .env.example .env
# Edite o arquivo .env e adicione uma SECRET_KEY
```

**Gerar SECRET_KEY:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Criar Diretórios
```powershell
New-Item -ItemType Directory -Force -Path logs
New-Item -ItemType Directory -Force -Path media
New-Item -ItemType Directory -Force -Path static
```

### 6. Migrar Banco de Dados
```powershell
python manage.py migrate
```

### 7. Popular Dados Iniciais
```powershell
python manage.py populate_data
```

### 8. Criar Superusuário
```powershell
python manage.py createsuperuser
```

### 9. Rodar Servidor
```powershell
python manage.py runserver
```

### 10. Acessar
- **Site:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/

## 🔧 Troubleshooting

### Problema: MySQL não conecta
**Solução:**
1. Verifique se o servidor MySQL está acessível: `10.54.4.7:3306`
2. Teste conexão: `Test-NetConnection -ComputerName 10.54.4.7 -Port 3306`
3. Verifique credenciais no arquivo `.env`

### Problema: Erro ao instalar mysqlclient
**Solução Windows:**
1. Instale Visual C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Ou instale binário pré-compilado:
```powershell
pip install https://download.lfd.uci.edu/pythonlibs/archived/mysqlclient-2.1.1-cp311-cp311-win_amd64.whl
```

### Problema: Pillow não instala
**Solução:**
```powershell
pip install --upgrade pip setuptools wheel
pip install Pillow
```

## 📞 Suporte

Se continuar com problemas:
1. Verifique versão do Python: `python --version` (mínimo 3.11)
2. Atualize pip: `python -m pip install --upgrade pip`
3. Verifique logs em: `logs/django.log`

---

**Após instalar o Python, execute os comandos da seção "Executar o Projeto" na ordem! 🎯**
