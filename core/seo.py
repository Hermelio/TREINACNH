"""
Centralized SEO configuration — title + meta description per page.

Titles ≤ 60 chars, descriptions ≤ 160 chars.
Used by views to inject `seo_title` and `seo_description` into the template context.
"""

# Static pages config
SEO_PAGES = {
    'core:home': {
        'title': 'Instrutor de Trânsito Autônomo Perto de Você | TreinaCNH',
        'description': (
            'Compare instrutores de trânsito autônomos credenciados na sua cidade. '
            'Veja avaliações, preços e agende aulas de direção particular pelo DETRAN.'
        ),
    },
    'core:about': {
        'title': 'Sobre a TreinaCNH | Plataforma de Instrutores Autônomos',
        'description': (
            'Conheça a TreinaCNH, plataforma que conecta alunos a instrutores de '
            'trânsito autônomos credenciados em todo o Brasil.'
        ),
    },
    'core:contact': {
        'title': 'Contato | TreinaCNH',
        'description': (
            'Entre em contato com a TreinaCNH. Suporte para instrutores autônomos '
            'e alunos. Respondemos em até 24 horas.'
        ),
    },
    'core:faq': {
        'title': 'Perguntas Frequentes sobre Aulas de Direção | TreinaCNH',
        'description': (
            'Tire dúvidas sobre instrutores autônomos, aulas práticas de CNH, '
            'preços e como funciona a plataforma TreinaCNH.'
        ),
    },
    'core:news_list': {
        'title': 'Notícias de Trânsito e DETRAN | TreinaCNH',
        'description': (
            'Acompanhe as últimas notícias sobre legislação de trânsito, '
            'habilitação CNH, multas e segurança nas estradas.'
        ),
    },
}

FALLBACK_TITLE = 'TreinaCNH - Instrutores de Trânsito Autônomos'
FALLBACK_DESCRIPTION = (
    'Encontre instrutores de trânsito autônomos credenciados perto de você. '
    'Compare preços, veja avaliações e agende aulas de direção particular.'
)


def get_page_seo(url_name: str) -> dict:
    """Returns {'seo_title': ..., 'seo_description': ...} for a static page."""
    seo = SEO_PAGES.get(url_name, {})
    return {
        'seo_title': seo.get('title', FALLBACK_TITLE),
        'seo_description': seo.get('description', FALLBACK_DESCRIPTION),
    }


def build_seo(title: str = None, description: str = None) -> dict:
    """
    Build SEO dict for dynamic pages (e.g. instructor profile, news article).
    Truncates title to 60 chars and description to 160 chars.
    """
    raw_title = (title or FALLBACK_TITLE).strip()
    raw_desc = (description or FALLBACK_DESCRIPTION).strip()

    seo_title = raw_title if len(raw_title) <= 60 else raw_title[:57].rstrip() + '...'
    seo_description = raw_desc if len(raw_desc) <= 160 else raw_desc[:157].rstrip() + '...'

    return {
        'seo_title': seo_title,
        'seo_description': seo_description,
    }
