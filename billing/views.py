"""
Views for billing app with Mercado Pago integration.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import mercadopago
import json
import logging

from .models import Plan, Subscription, Payment, PaymentStatusChoices, PaymentMethodChoices
from marketplace.models import InstructorProfile

logger = logging.getLogger(__name__)


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

@login_required
def checkout_view(request, subscription_id):
    """
    Create Mercado Pago preference and show checkout page.
    """
    # Verify instructor
    if not request.user.profile.is_instructor:
        messages.error(request, 'Apenas instrutores podem acessar esta página.')
        return redirect('accounts:dashboard')
    
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
    except InstructorProfile.DoesNotExist:
        messages.error(request, 'Perfil de instrutor não encontrado.')
        return redirect('accounts:dashboard')
    
    # Get subscription
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        instructor=instructor_profile
    )
    
    # Check if already has pending payment
    pending_payment = subscription.payments.filter(
        status=PaymentStatusChoices.PENDING
    ).first()
    
    if pending_payment and pending_payment.preference_id:
        # Reuse existing preference
        preference_id = pending_payment.preference_id
    else:
        # Create new Mercado Pago preference
        try:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            preference_data = {
                "items": [
                    {
                        "title": f"{subscription.plan.name} - TreinaCNH",
                        "quantity": 1,
                        "unit_price": float(subscription.plan.price_monthly),
                        "currency_id": "BRL",
                        "description": f"Renovação de assinatura - {subscription.plan.name}"
                    }
                ],
                "payer": {
                    "name": request.user.first_name,
                    "surname": request.user.last_name,
                    "email": request.user.email,
                },
                "back_urls": {
                    "success": f"{settings.SITE_URL}/pagamento/sucesso/",
                    "failure": f"{settings.SITE_URL}/pagamento/falha/",
                    "pending": f"{settings.SITE_URL}/pagamento/pendente/"
                },
                "auto_return": "approved",
                "notification_url": f"{settings.SITE_URL}/webhook/mercadopago/",
                "external_reference": f"subscription_{subscription.id}",
                "statement_descriptor": "TREINACNH",
            }
            
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            preference_id = preference["id"]
            
            # Create or update payment record
            if pending_payment:
                pending_payment.preference_id = preference_id
                pending_payment.save()
            else:
                Payment.objects.create(
                    subscription=subscription,
                    amount=subscription.plan.price_monthly,
                    payment_method=PaymentMethodChoices.PIX,
                    status=PaymentStatusChoices.PENDING,
                    external_id=f"pending_{subscription.id}_{timezone.now().timestamp()}",
                    preference_id=preference_id
                )
            
            logger.info(f"Preference created: {preference_id} for subscription {subscription.id}")
            
        except Exception as e:
            logger.error(f"Error creating Mercado Pago preference: {str(e)}")
            messages.error(request, 'Erro ao criar pagamento. Tente novamente.')
            return redirect('billing:my_subscription')
    
    context = {
        'subscription': subscription,
        'preference_id': preference_id,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
        'page_title': 'Renovar Assinatura',
    }
    return render(request, 'billing/checkout.html', context)


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    """
    Handle Mercado Pago webhook notifications.
    """
    try:
        # Parse webhook data
        data = json.loads(request.body)
        logger.info(f"Webhook received: {data}")
        
        # Check notification type
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if not payment_id:
                logger.warning("No payment ID in webhook")
                return HttpResponse(status=400)
            
            # Get payment details from Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            payment_data = payment_info["response"]
            
            logger.info(f"Payment data: {payment_data}")
            
            # Get subscription from external_reference
            external_ref = payment_data.get('external_reference', '')
            if not external_ref.startswith('subscription_'):
                logger.warning(f"Invalid external reference: {external_ref}")
                return HttpResponse(status=200)
            
            subscription_id = external_ref.replace('subscription_', '')
            
            try:
                subscription = Subscription.objects.get(id=subscription_id)
            except Subscription.DoesNotExist:
                logger.error(f"Subscription not found: {subscription_id}")
                return HttpResponse(status=404)
            
            # Update or create payment record
            payment, created = Payment.objects.update_or_create(
                external_id=str(payment_id),
                defaults={
                    'subscription': subscription,
                    'amount': payment_data.get('transaction_amount', 0),
                    'payment_method': payment_data.get('payment_method_id', 'unknown').upper(),
                    'status': payment_data.get('status', 'pending').upper(),
                    'payment_details': payment_data,
                    'paid_at': timezone.now() if payment_data.get('status') == 'approved' else None
                }
            )
            
            # If approved, extend subscription
            if payment_data.get('status') == 'approved':
                if subscription.end_date:
                    # Extend from current end date
                    new_end_date = subscription.end_date + timedelta(days=30)
                else:
                    # Start from today
                    new_end_date = timezone.now().date() + timedelta(days=30)
                
                subscription.end_date = new_end_date
                subscription.status = 'ACTIVE'
                subscription.save()
                
                logger.info(f"Subscription {subscription.id} extended to {new_end_date}")
                
                # TODO: Send confirmation email
                # send_payment_confirmation_email(subscription, payment)
            
            return HttpResponse(status=200)
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=500)


@login_required
def payment_success_view(request):
    """Payment success page"""
    messages.success(request, 'Pagamento realizado com sucesso! Sua assinatura foi renovada.')
    return redirect('billing:my_subscription')


@login_required
def payment_failure_view(request):
    """Payment failure page"""
    messages.error(request, 'Pagamento não foi aprovado. Tente novamente ou escolha outro método.')
    return redirect('billing:my_subscription')


@login_required
def payment_pending_view(request):
    """Payment pending page"""
    messages.info(request, 'Pagamento pendente. Você receberá uma confirmação quando for aprovado.')
    return redirect('billing:my_subscription')