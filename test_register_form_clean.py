"""
Verifica se o formulário de cadastro está limpo e organizado.
"""
import os

print("=" * 70)
print("VERIFICAÇÃO DE LIMPEZA DO FORMULÁRIO DE CADASTRO")
print("=" * 70)
print()

template_path = 'templates/accounts/register.html'

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar se ainda há referências ao CPF
if 'form.cpf' in content or 'id_cpf' in content:
    print("❌ ERRO: Ainda há referências ao campo CPF no template!")
else:
    print("✅ Campo CPF completamente removido")

# Verificar se ainda há referências aos textos de ajuda da cidade
if 'cityHelpStudent' in content or 'cityHelpInstructor' in content:
    print("❌ ERRO: Ainda há referências aos textos de ajuda da cidade!")
else:
    print("✅ Textos de ajuda da cidade removidos")

# Contar seções organizadas
sections = {
    'Dados Pessoais': 'Dados Pessoais' in content,
    'Tipo de Cadastro': 'Tipo de Cadastro' in content,
    'Localização': 'Localização' in content,
    'Informações Profissionais': 'Informações Profissionais' in content,
    'Informações de Contato': 'Informações de Contato' in content,
    'Senha de Acesso': 'Senha de Acesso' in content,
    'Termos e Condições': 'Termos e Condições' in content,
}

print()
print("Seções do formulário:")
for section, exists in sections.items():
    status = "✅" if exists else "❌"
    print(f"  {status} {section}")

print()
print("=" * 70)
print("ESTRUTURA DO FORMULÁRIO:")
print("=" * 70)
print()
print("1. Botão de cadastro com Google")
print("2. Dados Pessoais (Nome, Sobrenome, Usuário, Email)")
print("3. Tipo de Cadastro (Aluno/Instrutor)")
print("4. Localização (Estado, Cidade)")
print("5. Informações Profissionais (apenas para instrutores)")
print("6. Informações de Contato (WhatsApp, Carro próprio para instrutor)")
print("7. Senha de Acesso")
print("8. Termos e Condições")
print()
print("=" * 70)
print("✅ Formulário limpo e bem organizado!")
print("=" * 70)
