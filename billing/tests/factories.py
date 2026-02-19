"""
Test factories para criar objetos de teste de forma consistente.
"""
import datetime
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Profile, RoleChoices
from marketplace.models import InstructorProfile, City, State
from billing.models import Plan, Subscription, Payment, PaymentStatusChoices, PaymentMethodChoices, SubscriptionStatusChoices


def make_state(name="São Paulo", code="SP"):
    state, _ = State.objects.get_or_create(code=code, defaults={"name": name})
    return state


def make_city(name="São Paulo", state=None):
    if state is None:
        state = make_state()
    # City.save() auto-gera slug, mas get_or_create exige slug ou unique_together
    city = City.objects.filter(name=name, state=state).first()
    if not city:
        city = City.objects.create(name=name, state=state)
    return city


def make_instructor_user(username="instrutor_test", email="instrutor@test.com"):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "first_name": "Instrutor", "last_name": "Teste"},
    )
    if created:
        user.set_password("senha123!")
        user.save()

    profile, _ = Profile.objects.get_or_create(user=user, defaults={"role": RoleChoices.INSTRUCTOR})
    if profile.role != RoleChoices.INSTRUCTOR:
        profile.role = RoleChoices.INSTRUCTOR
        profile.save()

    city = make_city()
    instructor, _ = InstructorProfile.objects.get_or_create(
        user=user,
        defaults={"city": city, "bio": "Bio de teste", "is_visible": True},
    )
    return user, instructor


def make_plan(name="Plano Teste", price=49.99):
    plan, _ = Plan.objects.get_or_create(
        name=name,
        defaults={
            "description": "Plano de teste",
            "price_monthly": price,
            "features": "Recurso 1\nRecurso 2",
            "is_active": True,
            "order": 1,
        },
    )
    return plan


def make_subscription(instructor=None, plan=None, status=SubscriptionStatusChoices.ACTIVE, days_from_now=30):
    if instructor is None:
        _, instructor = make_instructor_user()
    if plan is None:
        plan = make_plan()
    today = datetime.date.today()
    sub, _ = Subscription.objects.get_or_create(
        instructor=instructor,
        plan=plan,
        defaults={
            "status": status,
            "start_date": today,
            "end_date": today + datetime.timedelta(days=days_from_now),
        },
    )
    return sub


def make_payment(subscription=None, external_id="pay_123", status=PaymentStatusChoices.PENDING, amount=None):
    if subscription is None:
        subscription = make_subscription()
    if amount is None:
        amount = subscription.plan.price_monthly
    payment, _ = Payment.objects.get_or_create(
        external_id=external_id,
        defaults={
            "subscription": subscription,
            "amount": amount,
            "payment_method": PaymentMethodChoices.CREDIT_CARD,
            "status": status,
            "preference_id": "pref_123",
        },
    )
    return payment


# ---------------------------------------------------------------------------
# Payloads fake do Mercado Pago
# ---------------------------------------------------------------------------

def mp_webhook_payload(payment_id=1234567890):
    """Payload que o MP envia via POST no webhook (notification)."""
    return {
        "type": "payment",
        "data": {"id": str(payment_id)},
        "action": "payment.created",
        "id": payment_id,
    }


def mp_payment_response(
    payment_id=1234567890,
    status="approved",
    status_detail="accredited",
    amount=49.99,
    collector_id=3161194628,
    live_mode=False,
    external_reference="subscription_1",
    payment_method_id="master",
):
    """Resposta fake da API GET /v1/payments/{id} do Mercado Pago."""
    return {
        "status": 200,
        "response": {
            "id": payment_id,
            "status": status,
            "status_detail": status_detail,
            "transaction_amount": amount,
            "collector_id": collector_id,
            "live_mode": live_mode,
            "external_reference": external_reference,
            "payment_method_id": payment_method_id,
            "payment_type_id": "credit_card",
            "date_approved": "2026-02-19T13:10:35.000-04:00",
            "date_created": "2026-02-19T13:10:35.000-04:00",
            "currency_id": "BRL",
            "transaction_details": {
                "net_received_amount": 48.01,
                "total_paid_amount": amount,
                "installment_amount": amount,
            },
        },
    }
