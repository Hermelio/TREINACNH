"""
Script to create Terms of Use page
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import StaticPage

# Terms content
terms_content = """
<div class="container py-5" style="padding-top: 7rem !important;">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <h1 class="mb-4">Termos de Uso — TreinaCNH</h1>
            <p class="text-muted mb-5"><strong>Última atualização:</strong> 11/12/2025</p>
            
            <div class="alert alert-info">
                <p class="mb-0">Bem-vindo à TreinaCNH. Ao utilizar nossa plataforma, você concorda com estes Termos de Uso. Leia com atenção.</p>
            </div>

            <section class="mb-5">
                <h2 class="h4 mb-3">1. Sobre a TreinaCNH</h2>
                <p>A TreinaCNH é uma plataforma digital que conecta alunos interessados em aulas de direção a instrutores autônomos.</p>
                <p><strong>A TreinaCNH não é uma autoescola</strong>, não oferece serviços de instrução de direção e não intermedeia pagamentos entre instrutores e alunos.</p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">2. Responsabilidade pelos Serviços</h2>
                <p>Os instrutores cadastrados são profissionais independentes, sendo totalmente responsáveis por:</p>
                <ul>
                    <li>qualidade, metodologia e segurança das aulas;</li>
                    <li>regularidade documental e credenciamento perante os órgãos competentes;</li>
                    <li>valores cobrados, horários e forma de atendimento;</li>
                    <li>comunicação e acordos realizados com seus alunos.</li>
                </ul>
                <p><strong>A TreinaCNH não garante, não fiscaliza e não responde por nenhum desses aspectos.</strong></p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">3. Limitação de Responsabilidade</h2>
                <p>A TreinaCNH não se responsabiliza por:</p>
                <ul>
                    <li>eventuais conflitos, atrasos, ausências, cancelamentos ou divergências entre alunos e instrutores;</li>
                    <li>danos materiais, morais ou pessoais decorrentes das aulas;</li>
                    <li>informações incorretas ou desatualizadas fornecidas pelos instrutores ou alunos.</li>
                </ul>
                <p><strong>A plataforma atua apenas como meio de conexão e divulgação.</strong></p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">4. Cadastro e Veracidade das Informações</h2>
                <p>Ao se cadastrar, o usuário (instrutor ou aluno) declara que:</p>
                <ul>
                    <li>todas as informações fornecidas são verdadeiras e atualizadas;</li>
                    <li>possui a documentação e os requisitos legais necessários para atuar (no caso dos instrutores).</li>
                </ul>
                <p>A TreinaCNH pode suspender ou excluir perfis que violem estes Termos.</p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">5. Período Grátis e Assinaturas (Instrutores)</h2>
                <p>Instrutores pioneiros podem receber um período gratuito conforme divulgado no site.</p>
                <p>Após esse período, a continuidade do uso depende da contratação de um plano pago.</p>
                <p>O não pagamento pode resultar na suspensão do perfil.</p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">6. Privacidade e Contato</h2>
                <p>Ao aceitar o uso da plataforma, o usuário concorda que a TreinaCNH poderá enviar comunicações por e-mail e WhatsApp, conforme autorizações concedidas no formulário de cadastro.</p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">7. Modificações nos Termos</h2>
                <p>A TreinaCNH pode alterar estes Termos a qualquer momento.</p>
                <p>As atualizações serão publicadas neste mesmo endereço, com nova data de revisão.</p>
            </section>

            <section class="mb-5">
                <h2 class="h4 mb-3">8. Aceitação</h2>
                <p>Ao utilizar a TreinaCNH, você confirma que leu, entendeu e concorda com estes Termos de Uso.</p>
                <div class="alert alert-warning mt-3">
                    <p class="mb-0"><strong>Ao usar o TreinaCNH, você reconhece que leu, entendeu e concorda em estar vinculado a estes Termos de Uso.</strong></p>
                </div>
            </section>
        </div>
    </div>
</div>
"""

# Create or update Terms page
page, created = StaticPage.objects.update_or_create(
    slug='termos',
    defaults={
        'title': 'Termos de Uso',
        'content': terms_content,
        'is_active': True
    }
)

if created:
    print(f"✓ Página de Termos criada com sucesso!")
else:
    print(f"✓ Página de Termos atualizada com sucesso!")

print(f"  URL: /pagina/termos/")
