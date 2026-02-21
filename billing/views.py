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
from django_ratelimit.decorators import ratelimit
import mercadopago
import json
import logging

from .models import Plan, Subscription, Payment, PaymentStatusChoices, PaymentMethodChoices, SubscriptionStatusChoices
from marketplace.models import InstructorProfile

logger = logging.getLogger(__name__)


def plans_view(request):
    """Public page showing available plans - only for instructors"""
    # Redirect students to marketplace
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role == 'STUDENT':
            messages.info(request, 'Planos são exclusivos para instrutores.')
            return redirect('marketplace:instructors_map')
    
    plans = Plan.objects.filter(is_active=True).order_by('order', 'price_monthly')
    
    # Check if user has active subscription and is instructor
    active_subscription = None
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.is_instructor:
        try:
            # Get instructor's active subscription
            active_subscription = Subscription.objects.filter(
                instructor__user=request.user,
                status=SubscriptionStatusChoices.ACTIVE
            ).select_related('plan').first()
        except Exception as e:
            logger.error(f"Error fetching subscription for user {request.user.id}: {str(e)}")
    
    context = {
        'plans': plans,
        'active_subscription': active_subscription,
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
    Accepts either subscription_id or plan_id (will create subscription if needed).
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
    
    # Try to get subscription, if not found, assume subscription_id is actually plan_id
    try:
        subscription = Subscription.objects.get(
            id=subscription_id,
            instructor=instructor_profile
        )
    except Subscription.DoesNotExist:
        # Assume it's a plan_id, create new subscription
        try:
            plan = Plan.objects.get(id=subscription_id)
            from datetime import date, timedelta
            # Check if already has an active subscription for this plan to avoid duplicates
            existing = Subscription.objects.filter(
                instructor=instructor_profile,
                plan=plan,
                status=SubscriptionStatusChoices.ACTIVE,
            ).first()
            if existing and existing.is_active:
                subscription = existing
                messages.info(request, f'Você já possui uma assinatura ativa do {plan.name}.')
            else:
                subscription = Subscription.objects.create(
                    instructor=instructor_profile,
                    plan=plan,
                    status='ACTIVE',
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=30)
                )
                messages.success(request, f'Assinatura do {plan.name} criada! Complete o pagamento.')
        except Plan.DoesNotExist:
            messages.error(request, 'Plano não encontrado.')
            return redirect('billing:plans')
    
    # Validate Mercado Pago configuration
    if not settings.MERCADOPAGO_ACCESS_TOKEN or not settings.MERCADOPAGO_PUBLIC_KEY:
        logger.error("Mercado Pago credentials not configured")
        messages.error(request, 'Sistema de pagamento não configurado. Contate o suporte.')
        return redirect('billing:plans')
    
    # Check if already has pending payment
    pending_payment = subscription.payments.filter(
        status=PaymentStatusChoices.PENDING
    ).first()
    
    init_point = None
    preference_id = None
    
    if pending_payment and pending_payment.preference_id:
        # Try to reuse existing preference
        preference_id = pending_payment.preference_id
        try:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            preference_response = sdk.preference().get(preference_id)
            if preference_response.get("status") == 200:
                init_point = preference_response["response"].get("init_point")
                logger.info(f"Reusing preference {preference_id} for subscription {subscription.id}")
            else:
                # If can't get old preference, create new one
                logger.warning(f"Could not retrieve preference {preference_id}, creating new one")
                pending_payment = None
                preference_id = None
        except Exception as e:
            logger.error(f"Error retrieving preference: {str(e)}")
            pending_payment = None
            preference_id = None
    
    if not pending_payment or not preference_id:
        # Create new Mercado Pago preference
        try:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            # Ensure user has email
            user_email = request.user.email or f"{request.user.username}@treinacnh.com.br"
            
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
                    "name": request.user.first_name or "Instrutor",
                    "surname": request.user.last_name or "TreinaCNH",
                    "email": user_email,
                },
                "payment_methods": {
                    "excluded_payment_methods": [],
                    "excluded_payment_types": [],
                    "installments": 12,  # Permite parcelamento em até 12x
                    "default_installments": 1
                },
                "back_urls": {
                    "success": f"{settings.SITE_URL}/planos/pagamento/sucesso/",
                    "failure": f"{settings.SITE_URL}/planos/pagamento/falha/",
                    "pending": f"{settings.SITE_URL}/planos/pagamento/pendente/"
                },
                "auto_return": "approved",
                "notification_url": f"{settings.SITE_URL}/webhook/mercadopago/",
                "external_reference": f"subscription_{subscription.id}",
                "statement_descriptor": "TREINACNH",
            }
            
            preference_response = sdk.preference().create(preference_data)
            
            # Log the response for debugging
            logger.info(f"Mercado Pago response status: {preference_response.get('status')}")
            logger.info(f"Mercado Pago response: {preference_response}")
            
            # Check if request was successful
            if preference_response["status"] != 201:
                error_msg = preference_response.get("response", {}).get("message", "Erro desconhecido")
                raise Exception(f"Mercado Pago retornou status {preference_response['status']}: {error_msg}")
            
            preference = preference_response["response"]
            preference_id = preference["id"]
            init_point = preference["init_point"]  # Get redirect URL
            
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
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error creating Mercado Pago preference: {str(e)}\n{error_details}")
            messages.error(request, f'Erro ao criar pagamento: {str(e)}')
            return redirect('billing:plans')
    
    context = {
        'subscription': subscription,
        'preference_id': preference_id,
        'init_point': init_point,
        'public_key': settings.MERCADOPAGO_PUBLIC_KEY,
        'page_title': 'Renovar Assinatura',
    }
    return render(request, 'billing/checkout.html', context)


@csrf_exempt
@require_POST
def mercadopago_webhook(request):
    """
    Handle Mercado Pago webhook notifications.
    Implements idempotency, validation and comprehensive error handling.
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

            # -------------------------------------------------------
            # IDEMPOTÊNCIA: ignorar se já aprovado (evita reprocessamento)
            # -------------------------------------------------------
            existing_payment = Payment.objects.filter(external_id=str(payment_id)).first()
            if existing_payment and existing_payment.status == PaymentStatusChoices.APPROVED:
                logger.info(f"Payment {payment_id} already processed and approved - skipping")
                return HttpResponse(status=200)

            # Get payment details from Mercado Pago
            try:
                sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                payment_info = sdk.payment().get(payment_id)

                if payment_info.get("status") != 200:
                    logger.error(f"Failed to get payment from MP: {payment_info}")
                    return HttpResponse(status=500)

                payment_data = payment_info["response"]
                logger.info(f"Payment data retrieved: ID={payment_id}, Status={payment_data.get('status')}, Detail={payment_data.get('status_detail')}")

            except Exception as e:
                logger.error(f"Error fetching payment from Mercado Pago: {str(e)}")
                return HttpResponse(status=500)

            # -------------------------------------------------------
            # VALIDAÇÃO 1: live_mode deve bater com o ambiente configurado
            # Só rejeita se AMBOS: produção E credencial for LIVE (não TEST)
            # -------------------------------------------------------
            is_production = not settings.DEBUG
            payment_live_mode = payment_data.get('live_mode', False)
            access_token = settings.MERCADOPAGO_ACCESS_TOKEN
            using_test_credentials = access_token.startswith('TEST-')
            # Apenas bloquear se: produção com credencial LIVE recebendo pagamento de teste
            # Não bloquear enquanto credenciais TEST estiverem em uso
            if is_production and not using_test_credentials and not payment_live_mode:
                logger.warning(f"Rejected test payment {payment_id} in production environment with live credentials")
                return HttpResponse(status=200)  # 200 para MP não retentar

            # -------------------------------------------------------
            # VALIDAÇÃO 2: collector_id deve ser nossa conta MP
            # -------------------------------------------------------
            expected_collector_id = getattr(settings, 'MERCADOPAGO_COLLECTOR_ID', None)
            actual_collector_id = payment_data.get('collector_id')
            if expected_collector_id and str(actual_collector_id) != str(expected_collector_id):
                logger.error(f"collector_id mismatch: expected {expected_collector_id}, got {actual_collector_id} for payment {payment_id}")
                return HttpResponse(status=200)

            # Get subscription from external_reference
            external_ref = payment_data.get('external_reference', '')
            if not external_ref or not external_ref.startswith('subscription_'):
                logger.warning(f"Invalid external reference: {external_ref}")
                return HttpResponse(status=200)

            subscription_id = external_ref.replace('subscription_', '')

            try:
                subscription = Subscription.objects.select_related('instructor', 'plan').get(id=subscription_id)
            except Subscription.DoesNotExist:
                logger.error(f"Subscription not found: {subscription_id}")
                return HttpResponse(status=404)
            except ValueError:
                logger.error(f"Invalid subscription ID format: {subscription_id}")
                return HttpResponse(status=400)

            # -------------------------------------------------------
            # VALIDAÇÃO 3: valor pago deve ser >= preço do plano
            # -------------------------------------------------------
            transaction_amount = float(payment_data.get('transaction_amount', 0))
            expected_amount = float(subscription.plan.price_monthly)
            if transaction_amount < expected_amount:
                logger.error(
                    f"Amount mismatch for payment {payment_id}: "
                    f"received R${transaction_amount:.2f}, expected R${expected_amount:.2f} "
                    f"for plan '{subscription.plan.name}'"
                )
                return HttpResponse(status=200)  # 200 para MP não retentar

            # Map MP payment method to our enum
            mp_method = payment_data.get('payment_method_id', 'unknown').upper()
            if 'PIX' in mp_method:
                payment_method = PaymentMethodChoices.PIX
            elif 'BOLETO' in mp_method or 'BOLBRADESCO' in mp_method:
                payment_method = PaymentMethodChoices.BOLETO
            elif 'CREDIT' in mp_method or any(card in mp_method for card in ['VISA', 'MASTER', 'AMEX', 'ELO']):
                payment_method = PaymentMethodChoices.CREDIT_CARD
            elif 'DEBIT' in mp_method or 'DEBITO' in mp_method:
                payment_method = PaymentMethodChoices.DEBIT_CARD
            else:
                payment_method = PaymentMethodChoices.CREDIT_CARD  # Fallback seguro

            # -------------------------------------------------------
            # VALIDAÇÃO 4: status + status_detail para aprovação real
            # Apenas status=approved E status_detail=accredited ativa assinatura
            # -------------------------------------------------------
            mp_status = payment_data.get('status', 'pending')
            mp_status_detail = payment_data.get('status_detail', '')

            is_truly_approved = (
                mp_status == 'approved' and
                mp_status_detail in ('accredited', 'partially_refunded')  # accredited = pago e creditado
            )

            status_map = {
                'pending': PaymentStatusChoices.PENDING,
                'approved': PaymentStatusChoices.APPROVED,
                'authorized': PaymentStatusChoices.APPROVED,
                'in_process': PaymentStatusChoices.PENDING,
                'in_mediation': PaymentStatusChoices.PENDING,
                'rejected': PaymentStatusChoices.REJECTED,
                'cancelled': PaymentStatusChoices.CANCELLED,
                'refunded': PaymentStatusChoices.REFUNDED,
                'charged_back': PaymentStatusChoices.REFUNDED,
            }
            payment_status = status_map.get(mp_status, PaymentStatusChoices.PENDING)

            # Update or create payment record
            payment, created = Payment.objects.update_or_create(
                external_id=str(payment_id),
                defaults={
                    'subscription': subscription,
                    'amount': transaction_amount,
                    'payment_method': payment_method,
                    'status': payment_status,
                    'payment_details': payment_data,
                    'paid_at': timezone.now() if is_truly_approved else None,
                }
            )

            action = "Created" if created else "Updated"
            logger.info(f"{action} payment {payment.id}: status={mp_status} detail={mp_status_detail} for subscription {subscription.id}")

            # Activate/extend subscription only when truly approved + accredited
            if is_truly_approved:
                old_end_date = subscription.end_date

                if subscription.end_date and subscription.end_date >= timezone.now().date():
                    new_end_date = subscription.end_date + timedelta(days=30)
                else:
                    new_end_date = timezone.now().date() + timedelta(days=30)

                subscription.end_date = new_end_date
                subscription.status = SubscriptionStatusChoices.ACTIVE
                subscription.save()

                logger.info(f"Subscription {subscription.id} extended: {old_end_date} -> {new_end_date}")

                # TODO: Send confirmation email
                try:
                    # send_payment_confirmation_email(subscription, payment)
                    pass
                except Exception as email_error:
                    logger.error(f"Failed to send confirmation email: {email_error}")

            elif payment_status == PaymentStatusChoices.REJECTED:
                logger.warning(f"Payment {payment_id} rejected (detail={mp_status_detail}) for subscription {subscription.id}")
                # TODO: send_payment_rejection_email(subscription, payment)

            return HttpResponse(status=200)

        # Handle other notification types (merchant_order, etc.) - always 200
        logger.info(f"Unhandled notification type: {data.get('type')}")
        return HttpResponse(status=200)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {str(e)}")
        return HttpResponse(status=200)  # 200 para MP não retentar
    except Exception as e:
        import traceback
        logger.error(f"Webhook error: {str(e)}\n{traceback.format_exc()}")
        return HttpResponse(status=200)  # 200 para MP não retentar em erros internos


@login_required
def payment_success_view(request):
    """Payment success page - processes MP return URL params to confirm payment immediately"""
    # MP sends these GET params on return: payment_id, status, external_reference, etc.
    mp_payment_id = request.GET.get('payment_id') or request.GET.get('collection_id')
    mp_status = request.GET.get('status') or request.GET.get('collection_status')
    external_reference = request.GET.get('external_reference', '')

    if mp_payment_id and mp_status == 'approved' and external_reference.startswith('subscription_'):
        try:
            subscription_id = external_reference.replace('subscription_', '')
            subscription = Subscription.objects.get(
                id=subscription_id,
                instructor__user=request.user
            )

            # Idempotência: se o webhook já processou e aprovou, não duplicar
            already_approved = Payment.objects.filter(
                external_id=str(mp_payment_id),
                status=PaymentStatusChoices.APPROVED
            ).exists()

            if not already_approved:
                # Verificar via API do MP se o status_detail é realmente 'accredited'
                try:
                    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                    payment_info = sdk.payment().get(mp_payment_id)
                    if payment_info.get('status') == 200:
                        pd = payment_info['response']
                        mp_status_detail = pd.get('status_detail', '')
                        transaction_amount = float(pd.get('transaction_amount', 0))
                        expected_amount = float(subscription.plan.price_monthly)
                        is_truly_approved = (
                            pd.get('status') == 'approved' and
                            mp_status_detail in ('accredited', 'partially_refunded') and
                            transaction_amount >= expected_amount
                        )
                    else:
                        is_truly_approved = False
                except Exception:
                    # Se não conseguir validar via API, confia no parâmetro da URL
                    is_truly_approved = True

                if is_truly_approved:
                    Payment.objects.update_or_create(
                        external_id=str(mp_payment_id),
                        defaults={
                            'subscription': subscription,
                            'amount': subscription.plan.price_monthly,
                            'status': PaymentStatusChoices.APPROVED,
                            'paid_at': timezone.now(),
                            'payment_method': PaymentMethodChoices.CREDIT_CARD,
                        }
                    )
                    from datetime import timedelta
                    if subscription.end_date and subscription.end_date >= timezone.now().date():
                        subscription.end_date = subscription.end_date + timedelta(days=30)
                    else:
                        subscription.end_date = timezone.now().date() + timedelta(days=30)
                    subscription.status = SubscriptionStatusChoices.ACTIVE
                    subscription.save()
                    logger.info(f"Payment {mp_payment_id} confirmed via back_url for subscription {subscription.id}")

            messages.success(request, f'🎉 Pagamento aprovado! Assinatura do {subscription.plan.name} renovada até {subscription.end_date.strftime("%d/%m/%Y")}.')
        except Exception as e:
            logger.error(f"Error processing success return from MP: {str(e)}")
            messages.success(request, 'Pagamento realizado com sucesso! Sua assinatura será ativada em instantes.')
    elif mp_status == 'pending':
        messages.info(request, 'Pagamento pendente de confirmação. Você receberá uma atualização em breve.')
    else:
        messages.success(request, 'Pagamento realizado! Sua assinatura será ativada em instantes.')

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


@login_required
def check_payment_status(request, payment_id):
    """
    Check payment status directly from Mercado Pago.
    Useful for manual verification.
    """
    if not request.user.profile.is_instructor:
        messages.error(request, 'Acesso negado.')
        return redirect('accounts:dashboard')
    
    try:
        payment = Payment.objects.get(id=payment_id)
        
        # Verify user owns this payment
        if payment.subscription.instructor.user != request.user:
            messages.error(request, 'Você não tem permissão para ver este pagamento.')
            return redirect('billing:my_subscription')
        
        # Query Mercado Pago for current status
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        payment_info = sdk.payment().get(payment.external_id)
        
        if payment_info.get("status") == 200:
            payment_data = payment_info["response"]
            current_status = payment_data.get('status', 'unknown')
            
            messages.info(request, f'Status atual no Mercado Pago: {current_status}')
            logger.info(f"Manual payment check: {payment.external_id} - Status: {current_status}")
        else:
            messages.error(request, 'Não foi possível verificar o status do pagamento.')
        
    except Payment.DoesNotExist:
        messages.error(request, 'Pagamento não encontrado.')
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        messages.error(request, 'Erro ao verificar status do pagamento.')
    
    return redirect('billing:my_subscription')


def validate_subscription_status():
    """
    Background task to check and update expired subscriptions.
    Should be called periodically (e.g., daily cron job).
    """
    from datetime import date
    
    expired_subscriptions = Subscription.objects.filter(
        status=SubscriptionStatusChoices.ACTIVE,
        end_date__lt=date.today()
    )
    
    count = 0
    for subscription in expired_subscriptions:
        subscription.status = SubscriptionStatusChoices.PAUSED
        subscription.save()
        count += 1
        logger.info(f"Paused expired subscription: {subscription.id}")
    
    logger.info(f"Validated subscriptions: {count} expired subscriptions paused")
    return count