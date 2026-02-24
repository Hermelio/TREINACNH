"""
Teste para verificar que o campo CPF foi removido dos formulários de aluno.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.forms import UserRegistrationForm, StudentDataForm

print("=" * 70)
print("VERIFICAÇÃO DE REMOÇÃO DO CAMPO CPF")
print("=" * 70)
print()

# Verificar UserRegistrationForm
print("📋 UserRegistrationForm (Cadastro de Usuário):")
reg_form = UserRegistrationForm()
if 'cpf' in reg_form.fields:
    print("   ❌ ERRO: Campo CPF ainda existe no formulário de registro!")
else:
    print("   ✅ Campo CPF removido com sucesso")
print()

# Verificar StudentDataForm
print("📋 StudentDataForm (Completar Dados do Aluno):")
student_form = StudentDataForm()
if 'cpf' in student_form.fields:
    print("   ❌ ERRO: Campo CPF ainda existe no formulário de dados do aluno!")
else:
    print("   ✅ Campo CPF removido com sucesso")
print()

# Listar campos ativos em cada formulário
print("-" * 70)
print("Campos ativos no UserRegistrationForm:")
for field_name in reg_form.fields.keys():
    print(f"   • {field_name}")
print()

print("Campos ativos no StudentDataForm:")
for field_name in student_form.fields.keys():
    print(f"   • {field_name}")
print()

print("=" * 70)
print("✅ Verificação concluída!")
print("=" * 70)
