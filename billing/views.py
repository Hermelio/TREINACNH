"""
Views for billing app.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Plan


def plans_view(request):
    """Public page showing available plans"""
    plans = Plan.objects.filter(is_active=True).order_by('order', 'price_monthly')
    
    context = {
        'plans': plans,
        'page_title': 'Planos para Instrutores',
    }
    return render(request, 'billing/plans.html', context)


@login_required
def my_subscription_view(request):
    """View current subscription (for instructors)"""
    if not request.user.profile.is_instructor:
        from django.contrib import messages
        messages.error(request, 'Apenas instrutores podem acessar esta página.')
        from django.shortcuts import redirect
        return redirect('accounts:dashboard')
    
    try:
        from marketplace.models import InstructorProfile
        instructor_profile = InstructorProfile.objects.get(user=request.user)
        subscriptions = instructor_profile.subscriptions.filter(status='ACTIVE').select_related('plan')
        highlights = instructor_profile.highlights.filter(is_active=True).select_related('city')
    except InstructorProfile.DoesNotExist:
        subscriptions = []
        highlights = []
    
    context = {
        'subscriptions': subscriptions,
        'highlights': highlights,
        'page_title': 'Minha Assinatura',
    }
    return render(request, 'billing/my_subscription.html', context)
