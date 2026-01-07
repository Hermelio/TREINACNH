"""
Template tags for verification badges and trust indicators.
"""
from django import template

register = template.Library()


@register.inclusion_tag('verification/badges/trust_badge.html')
def trust_score_badge(user):
    """
    Display trust score badge with color and icon.
    Usage: {% trust_score_badge user %}
    """
    score = user.profile.trust_score
    
    if score >= 80:
        level = 'high'
        color = 'success'
        icon = 'shield-check'
        text = 'Confiável'
    elif score >= 60:
        level = 'medium'
        color = 'warning'
        icon = 'shield'
        text = 'Verificado'
    elif score >= 40:
        level = 'low'
        color = 'info'
        icon = 'shield-exclamation'
        text = 'Em Verificação'
    else:
        level = 'very-low'
        color = 'danger'
        icon = 'shield-x'
        text = 'Não Verificado'
    
    return {
        'score': score,
        'level': level,
        'color': color,
        'icon': icon,
        'text': text
    }


@register.inclusion_tag('verification/badges/verification_badges.html')
def verification_badges(user):
    """
    Display all verification badges (email, phone, identity, document).
    Usage: {% verification_badges user %}
    """
    badges = []
    
    # Email verified
    if user.profile.email_verified:
        badges.append({
            'icon': 'envelope-check',
            'color': 'success',
            'text': 'Email Verificado',
            'verified': True
        })
    else:
        badges.append({
            'icon': 'envelope',
            'color': 'secondary',
            'text': 'Email Não Verificado',
            'verified': False
        })
    
    # Phone verified
    if user.profile.phone_verified:
        badges.append({
            'icon': 'phone-check',
            'color': 'success',
            'text': 'Telefone Verificado',
            'verified': True
        })
    else:
        badges.append({
            'icon': 'phone',
            'color': 'secondary',
            'text': 'Telefone Não Verificado',
            'verified': False
        })
    
    # Identity verified
    if user.profile.identity_verified:
        badges.append({
            'icon': 'person-check',
            'color': 'success',
            'text': 'Identidade Verificada',
            'verified': True
        })
    else:
        badges.append({
            'icon': 'person',
            'color': 'secondary',
            'text': 'Identidade Não Verificada',
            'verified': False
        })
    
    # Document verified (for instructors only)
    if hasattr(user, 'instructor_profile'):
        from verification.models import InstructorDocument
        has_approved = InstructorDocument.objects.filter(
            instructor=user.instructor_profile,
            status='APPROVED'
        ).exists()
        
        if has_approved:
            badges.append({
                'icon': 'file-earmark-check',
                'color': 'success',
                'text': 'Documentos Aprovados',
                'verified': True
            })
        else:
            badges.append({
                'icon': 'file-earmark',
                'color': 'secondary',
                'text': 'Documentos Pendentes',
                'verified': False
            })
    
    return {'badges': badges}


@register.filter
def trust_level_text(score):
    """
    Convert trust score to text description.
    Usage: {{ user.profile.trust_score|trust_level_text }}
    """
    if score >= 80:
        return 'Altamente Confiável'
    elif score >= 60:
        return 'Confiável'
    elif score >= 40:
        return 'Moderado'
    else:
        return 'Baixa Confiança'


@register.filter
def trust_level_color(score):
    """
    Get Bootstrap color class for trust score.
    Usage: {{ user.profile.trust_score|trust_level_color }}
    """
    if score >= 80:
        return 'success'
    elif score >= 60:
        return 'primary'
    elif score >= 40:
        return 'warning'
    else:
        return 'danger'


@register.simple_tag
def verification_progress(user):
    """
    Calculate verification progress percentage.
    Usage: {% verification_progress user as progress %}
    """
    steps = [
        user.email and user.email != '',  # Has email
        user.profile.email_verified,
        user.profile.phone and user.profile.phone != '',  # Has phone
        user.profile.phone_verified,
        user.profile.identity_verified,
    ]
    
    # Add document verification for instructors
    if hasattr(user, 'instructor_profile'):
        from verification.models import InstructorDocument
        has_doc = InstructorDocument.objects.filter(
            instructor=user.instructor_profile,
            status='APPROVED'
        ).exists()
        steps.append(has_doc)
    
    completed = sum(1 for step in steps if step)
    total = len(steps)
    
    return round((completed / total) * 100)


@register.inclusion_tag('verification/badges/security_alerts.html')
def security_alerts(user):
    """
    Show security alerts if any.
    Usage: {% security_alerts user %}
    """
    from verification.models_security import SuspiciousActivity
    
    alerts = []
    
    # Check if blocked
    if user.profile.is_blocked:
        alerts.append({
            'type': 'danger',
            'icon': 'exclamation-triangle',
            'message': f'Conta bloqueada: {user.profile.block_reason}'
        })
    
    # Check unreviewed suspicious activities
    suspicious = SuspiciousActivity.objects.filter(
        user=user,
        reviewed=False,
        severity__in=['HIGH', 'CRITICAL']
    ).count()
    
    if suspicious > 0:
        alerts.append({
            'type': 'warning',
            'icon': 'shield-exclamation',
            'message': f'{suspicious} atividade(s) suspeita(s) detectada(s)'
        })
    
    # Check low trust score
    if user.profile.trust_score < 40:
        alerts.append({
            'type': 'info',
            'icon': 'info-circle',
            'message': 'Complete as verificações para aumentar sua confiabilidade'
        })
    
    return {'alerts': alerts}
