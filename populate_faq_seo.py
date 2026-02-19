"""
Script para popular as FAQs SEO no banco de dados.
Uso: python populate_faq_seo.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import FAQEntry

faqs = [
    # --- Para Alunos ---
    {
        'question': 'Como encontrar um instrutor de trânsito autônomo perto de mim?',
        'answer': 'Na TreinaCNH, basta informar sua cidade ou estado na página inicial e você verá todos os instrutores autônomos credenciados disponíveis na sua região. É possível comparar preços, ver avaliações de outros alunos e entrar em contato diretamente com o instrutor.',
        'category': 'STUDENT',
        'order': 1,
    },
    {
        'question': 'Quanto custa uma aula de direção particular?',
        'answer': 'O valor varia conforme a cidade, o instrutor e o tipo de veículo. Em média, aulas de direção particular custam entre R$ 80 e R$ 200 por hora. Consulte o perfil de cada instrutor na plataforma para ver os preços atualizados e pacotes disponíveis.',
        'category': 'STUDENT',
        'order': 2,
    },
    {
        'question': 'Qual a diferença entre instrutor autônomo e autoescola?',
        'answer': 'O instrutor autônomo é um profissional credenciado pelo DETRAN que oferece aulas práticas de forma independente, sem vínculo com uma autoescola. Ele costuma ter maior flexibilidade de horários, preços mais acessíveis e atendimento mais personalizado. A autoescola oferece o processo completo (teórico + prático), enquanto o instrutor autônomo foca nas aulas práticas.',
        'category': 'STUDENT',
        'order': 3,
    },
    {
        'question': 'O instrutor autônomo precisa ser credenciado pelo DETRAN?',
        'answer': 'Sim. Para atuar legalmente, o instrutor autônomo precisa ter carteira de habilitação com as categorias que leciona, certificação como Instrutor de Trânsito pelo DETRAN e estar regularmente credenciado. Na TreinaCNH, verificamos a documentação de todos os instrutores cadastrados.',
        'category': 'STUDENT',
        'order': 4,
    },
    {
        'question': 'Posso fazer apenas aulas práticas com instrutor autônomo sem estar matriculado em autoescola?',
        'answer': 'Depende do estado. Em muitos estados brasileiros, o aluno pode contratar um instrutor autônomo para aulas práticas de reciclagem ou aperfeiçoamento. Para a primeira habilitação, geralmente é necessário estar matriculado em uma autoescola. Consulte a legislação do seu estado ou verifique com o instrutor.',
        'category': 'STUDENT',
        'order': 5,
    },
    {
        'question': 'Como entro em contato com um instrutor de trânsito?',
        'answer': 'Basta acessar o perfil do instrutor na TreinaCNH e clicar em "Entrar em contato". Você será direcionado para o WhatsApp ou e-mail do instrutor para combinar horários, preços e demais detalhes das aulas.',
        'category': 'STUDENT',
        'order': 6,
    },
    # --- Para Instrutores ---
    {
        'question': 'Como me cadastrar como instrutor autônomo na TreinaCNH?',
        'answer': 'O cadastro é simples: clique em "Seja Instrutor", preencha seus dados pessoais e profissionais, faça o upload dos documentos exigidos (CNH, certificado de instrutor, etc.) e aguarde a verificação da nossa equipe. Após aprovação, seu perfil fica visível para milhares de alunos em busca de instrutor.',
        'category': 'INSTRUCTOR',
        'order': 1,
    },
    {
        'question': 'Quanto custa para anunciar na plataforma TreinaCNH?',
        'answer': 'Oferecemos planos mensais com diferentes benefícios. Acesse a página de Planos para ver os valores atualizados e escolher o que melhor se adapta ao seu perfil. Há opções para instrutores iniciantes e para quem já tem uma carteira de alunos consolidada.',
        'category': 'INSTRUCTOR',
        'order': 2,
    },
    {
        'question': 'Preciso de CNPJ para me cadastrar como instrutor?',
        'answer': 'Não é obrigatório. Instrutores autônomos podem se cadastrar como pessoa física (CPF). O CNPJ é opcional e pode ser adicionado caso você prefira emitir notas fiscais de serviço pelos atendimentos.',
        'category': 'INSTRUCTOR',
        'order': 3,
    },
    {
        'question': 'Como recebo os contatos dos alunos interessados?',
        'answer': 'Quando um aluno se interessa pelo seu perfil, ele pode entrar em contato via WhatsApp ou e-mail diretamente. Dependendo do plano contratado, você também recebe notificações de alunos na sua cidade que estão buscando instrutor.',
        'category': 'INSTRUCTOR',
        'order': 4,
    },
    # --- Geral ---
    {
        'question': 'O que é a TreinaCNH?',
        'answer': 'A TreinaCNH é uma plataforma que conecta instrutores de trânsito autônomos credenciados a alunos que buscam aulas de direção particular em todo o Brasil. Nossa missão é facilitar o encontro entre quem quer aprender a dirigir e quem tem experiência para ensinar, com segurança e transparência.',
        'category': 'GENERAL',
        'order': 1,
    },
    {
        'question': 'A plataforma TreinaCNH funciona em todo o Brasil?',
        'answer': 'Sim! A TreinaCNH atende instrutores e alunos em todos os estados brasileiros. Você pode buscar instrutores por estado e cidade, e novos profissionais estão se cadastrando diariamente para ampliar a cobertura em todas as regiões.',
        'category': 'GENERAL',
        'order': 2,
    },
]

created = 0
updated = 0

for faq_data in faqs:
    obj, created_flag = FAQEntry.objects.update_or_create(
        question=faq_data['question'],
        defaults={
            'answer': faq_data['answer'],
            'category': faq_data['category'],
            'order': faq_data['order'],
            'is_active': True,
        }
    )
    if created_flag:
        created += 1
        print(f"  [CRIADO] [{faq_data['category']}] {faq_data['question'][:70]}...")
    else:
        updated += 1
        print(f"  [ATUALIZADO] [{faq_data['category']}] {faq_data['question'][:70]}...")

print(f"\nConcluído: {created} criadas, {updated} atualizadas. Total: {FAQEntry.objects.filter(is_active=True).count()} FAQs ativas.")
