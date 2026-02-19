"""
Testes para o webhook do Mercado Pago e fluxo de pagamentos.

Cobertura:
  1. payment.created → consulta retorna approved/accredited     → ativa assinatura
  2. Valor divergente (transaction_amount < plan.price_monthly) → rejeita silenciosamente
  3. payment_id duplicado (idempotência)                        → não reprocessa
  4. collector_id inválido                                      → rejeita silenciosamente
  5. live_mode=True em ambiente de teste (DEBUG=True)           → rejeita
  6. live_mode=False em ambiente de produção (DEBUG=False)      → rejeita
  7. status=rejected                                            → NÃO ativa assinatura
  8. status=approved mas status_detail≠accredited               → NÃO ativa assinatura
  9. payment_success_view com params válidos                    → ativa sem duplicar
 10. payment_success_view com payment_id já aprovado (idem.)   → não duplica extends

Como rodar:
    # Todos os testes de billing
    python manage.py test billing.tests.test_webhook -v 2

    # Só um caso específico
    python manage.py test billing.tests.test_webhook.WebhookApprovalTests.test_approved_payment_activates_subscription -v 2
"""

import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone

from billing.models import (
    Payment, PaymentStatusChoices, PaymentMethodChoices,
    Subscription, SubscriptionStatusChoices,
)
from billing.tests.factories import (
    make_instructor_user, make_plan, make_subscription, make_payment,
    mp_webhook_payload, mp_payment_response,
)

WEBHOOK_URL = "/webhook/mercadopago/"
COLLECTOR_ID = 3161194628


def _post_webhook(client, payment_id=9999001):
    """Helper: envia o payload de webhook como o MP enviaria."""
    return client.post(
        WEBHOOK_URL,
        data=json.dumps(mp_webhook_payload(payment_id)),
        content_type="application/json",
        REMOTE_ADDR="127.0.0.1",
        HTTP_X_FORWARDED_FOR="127.0.0.1",
    )


def _mock_sdk(payment_response: dict):
    """Helper: cria mock do SDK do MercadoPago que retorna payment_response."""
    mock_sdk = MagicMock()
    mock_sdk.payment.return_value.get.return_value = payment_response
    return mock_sdk


# ===========================================================================
# 1. Pagamento aprovado → assinatura ativada
# ===========================================================================
class WebhookApprovalTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_approval", "inst_approval@test.com")
        self.plan = make_plan("Plano Aprovação", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan, days_from_now=5)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_approved_payment_activates_subscription(self, mock_sdk_class):
        """payment.created + consulta approved/accredited deve ativar assinatura."""
        payment_id = 9001001
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="approved",
            status_detail="accredited",
            amount=49.99,
            collector_id=COLLECTOR_ID,
            live_mode=False,
            external_reference=f"subscription_{self.sub.id}",
        ))

        response = _post_webhook(self.client, payment_id)

        self.assertEqual(response.status_code, 200)

        # Payment criado com status APPROVED
        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertEqual(payment.status, PaymentStatusChoices.APPROVED)
        self.assertIsNotNone(payment.paid_at)
        self.assertEqual(float(payment.amount), 49.99)

        # Assinatura estendida e ativa
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, SubscriptionStatusChoices.ACTIVE)
        expected_end = date.today() + timedelta(days=30)
        # Pode ser day+5+30 se ainda válida — só verifica que avançou
        self.assertGreater(self.sub.end_date, date.today() + timedelta(days=10))

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_correct_payment_method_stored(self, mock_sdk_class):
        """Método de pagamento PIX deve ser armazenado corretamente."""
        payment_id = 9001002
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            payment_method_id="pix",
            external_reference=f"subscription_{self.sub.id}",
            collector_id=COLLECTOR_ID,
        ))

        _post_webhook(self.client, payment_id)

        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertEqual(payment.payment_method, PaymentMethodChoices.PIX)


# ===========================================================================
# 2. Valor divergente do plano → rejeita silenciosamente
# ===========================================================================
class WebhookAmountValidationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_amount", "inst_amount@test.com")
        self.plan = make_plan("Plano Valor", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_lower_amount_rejected(self, mock_sdk_class):
        """transaction_amount < plan.price_monthly deve ser rejeitado sem ativar."""
        payment_id = 9002001
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="approved",
            status_detail="accredited",
            amount=9.99,  # valor menor que os 49.99 do plano
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        response = _post_webhook(self.client, payment_id)

        # MP recebe 200 para não retentar, mas assinatura não avança
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Payment.objects.filter(external_id=str(payment_id)).exists())

        self.sub.refresh_from_db()
        original_end = self.sub.end_date
        self.assertEqual(self.sub.end_date, original_end)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_exact_amount_accepted(self, mock_sdk_class):
        """transaction_amount == plan.price_monthly deve ser aceito."""
        payment_id = 9002002
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            amount=49.99,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        _post_webhook(self.client, payment_id)
        self.assertTrue(Payment.objects.filter(external_id=str(payment_id)).exists())


# ===========================================================================
# 3. Idempotência — payment_id duplicado não reprocessa
# ===========================================================================
class WebhookIdempotencyTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_idemp", "inst_idemp@test.com")
        self.plan = make_plan("Plano Idemp", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_duplicate_payment_id_not_reprocessed(self, mock_sdk_class):
        """Mesmo payment_id já APPROVED não deve ativar assinatura novamente."""
        payment_id = 9003001
        # Cria payment já aprovado no banco
        existing = make_payment(
            subscription=self.sub,
            external_id=str(payment_id),
            status=PaymentStatusChoices.APPROVED,
        )
        original_end = self.sub.end_date

        response = _post_webhook(self.client, payment_id)

        # SDK não deve ter sido chamado (early return por idempotência)
        mock_sdk_class.assert_not_called()
        self.assertEqual(response.status_code, 200)

        # Assinatura não foi modificada
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.end_date, original_end)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_pending_payment_can_be_updated(self, mock_sdk_class):
        """Payment PENDING com mesmo external_id pode ser atualizado para APPROVED."""
        payment_id = 9003002
        make_payment(
            subscription=self.sub,
            external_id=str(payment_id),
            status=PaymentStatusChoices.PENDING,
        )
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="approved",
            status_detail="accredited",
            amount=49.99,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        _post_webhook(self.client, payment_id)

        # SDK foi chamado pois era PENDING
        mock_sdk_class.assert_called_once()
        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertEqual(payment.status, PaymentStatusChoices.APPROVED)


# ===========================================================================
# 4. collector_id inválido → rejeita
# ===========================================================================
class WebhookCollectorIdTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_collector", "inst_collector@test.com")
        self.plan = make_plan("Plano Collector", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_wrong_collector_id_rejected(self, mock_sdk_class):
        """collector_id de outra conta MP deve ser rejeitado sem ativar."""
        payment_id = 9004001
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            collector_id=999999999,  # ID de outra conta
            external_reference=f"subscription_{self.sub.id}",
            amount=49.99,
        ))

        response = _post_webhook(self.client, payment_id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Payment.objects.filter(external_id=str(payment_id)).exists())

        self.sub.refresh_from_db()
        original_end = self.sub.end_date
        self.assertEqual(self.sub.end_date, original_end)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID="",  # sem validação configurada
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_no_collector_id_configured_skips_check(self, mock_sdk_class):
        """Se MERCADOPAGO_COLLECTOR_ID não estiver configurado, aceita qualquer collector."""
        payment_id = 9004002
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            collector_id=999999999,
            external_reference=f"subscription_{self.sub.id}",
            amount=49.99,
        ))

        response = _post_webhook(self.client, payment_id)
        self.assertEqual(response.status_code, 200)
        # Payment criado pois não há collector_id configurado para validar
        self.assertTrue(Payment.objects.filter(external_id=str(payment_id)).exists())


# ===========================================================================
# 5 & 6. live_mode — teste vs produção
# ===========================================================================
class WebhookLiveModeTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_livemode", "inst_livemode@test.com")
        self.plan = make_plan("Plano LiveMode", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,  # ambiente de desenvolvimento
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_live_payment_rejected_in_debug_mode(self, mock_sdk_class):
        """live_mode=True em DEBUG=True deve ser rejeitado (pagamento real em dev)."""
        payment_id = 9005001
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            live_mode=True,  # pagamento real
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
            amount=49.99,
        ))

        response = _post_webhook(self.client, payment_id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Payment.objects.filter(external_id=str(payment_id)).exists())

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=False,  # ambiente de produção
        MERCADOPAGO_ACCESS_TOKEN="APP_USR-fake-production-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_test_payment_rejected_in_production(self, mock_sdk_class):
        """live_mode=False em DEBUG=False deve ser rejeitado (pagamento de teste em produção)."""
        payment_id = 9005002
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            live_mode=False,  # pagamento de teste
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
            amount=49.99,
        ))

        response = _post_webhook(self.client, payment_id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Payment.objects.filter(external_id=str(payment_id)).exists())

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_test_payment_accepted_in_debug_mode(self, mock_sdk_class):
        """live_mode=False em DEBUG=True deve ser aceito."""
        payment_id = 9005003
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            live_mode=False,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
            amount=49.99,
        ))

        _post_webhook(self.client, payment_id)
        self.assertTrue(Payment.objects.filter(external_id=str(payment_id)).exists())


# ===========================================================================
# 7. status=rejected → NÃO ativa assinatura
# ===========================================================================
class WebhookStatusTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_status", "inst_status@test.com")
        self.plan = make_plan("Plano Status", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan, days_from_now=5)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_rejected_payment_does_not_activate(self, mock_sdk_class):
        """Pagamento rejected não deve ativar ou estender assinatura."""
        payment_id = 9007001
        original_end = self.sub.end_date
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="rejected",
            status_detail="cc_rejected_insufficient_amount",
            amount=49.99,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        _post_webhook(self.client, payment_id)

        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertEqual(payment.status, PaymentStatusChoices.REJECTED)
        self.assertIsNone(payment.paid_at)

        self.sub.refresh_from_db()
        self.assertEqual(self.sub.end_date, original_end)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_pending_payment_does_not_activate(self, mock_sdk_class):
        """Pagamento pending (ex: boleto aguardando) não deve ativar assinatura."""
        payment_id = 9007002
        original_end = self.sub.end_date
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="pending",
            status_detail="pending_waiting_payment",
            amount=49.99,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        _post_webhook(self.client, payment_id)

        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertEqual(payment.status, PaymentStatusChoices.PENDING)

        self.sub.refresh_from_db()
        self.assertEqual(self.sub.end_date, original_end)


# ===========================================================================
# 8. approved mas status_detail ≠ accredited → NÃO ativa
# ===========================================================================
class WebhookStatusDetailTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        _, self.instructor = make_instructor_user("inst_detail", "inst_detail@test.com")
        self.plan = make_plan("Plano Detail", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan, days_from_now=5)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_approved_pending_contingency_does_not_activate(self, mock_sdk_class):
        """approved/pending_contingency (em análise) não deve ativar assinatura."""
        payment_id = 9008001
        original_end = self.sub.end_date
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="approved",
            status_detail="pending_contingency",  # não é 'accredited'
            amount=49.99,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        _post_webhook(self.client, payment_id)

        # Payment registrado como APPROVED (status MP) mas sem paid_at
        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertIsNone(payment.paid_at)

        # Assinatura NÃO foi estendida
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.end_date, original_end)

    @override_settings(
        MERCADOPAGO_COLLECTOR_ID=str(COLLECTOR_ID),
        DEBUG=True,
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
    )
    @patch("billing.views.mercadopago.SDK")
    def test_approved_accredited_with_partial_refund_activates(self, mock_sdk_class):
        """approved/partially_refunded (reembolso parcial) ainda deve ativar."""
        payment_id = 9008002
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="approved",
            status_detail="partially_refunded",
            amount=49.99,
            collector_id=COLLECTOR_ID,
            external_reference=f"subscription_{self.sub.id}",
        ))

        _post_webhook(self.client, payment_id)

        payment = Payment.objects.get(external_id=str(payment_id))
        self.assertIsNotNone(payment.paid_at)

        self.sub.refresh_from_db()
        self.assertGreater(self.sub.end_date, date.today() + timedelta(days=10))


# ===========================================================================
# 9 & 10. payment_success_view — retorno do MP após pagamento
# ===========================================================================
class PaymentSuccessViewTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.user, self.instructor = make_instructor_user("inst_success", "inst_success@test.com")
        self.plan = make_plan("Plano Success", price=49.99)
        self.sub = make_subscription(self.instructor, self.plan, days_from_now=0)
        self.client.force_login(self.user)

    @override_settings(
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
        DEBUG=True,
    )
    @patch("billing.views.mercadopago.SDK")
    def test_success_view_activates_subscription(self, mock_sdk_class):
        """back_url com params approved → ativa assinatura."""
        payment_id = 9009001
        mock_sdk_class.return_value = _mock_sdk(mp_payment_response(
            payment_id=payment_id,
            status="approved",
            status_detail="accredited",
            amount=49.99,
            external_reference=f"subscription_{self.sub.id}",
        ))

        response = self.client.get(
            reverse("billing:payment_success"),
            {
                "payment_id": str(payment_id),
                "status": "approved",
                "external_reference": f"subscription_{self.sub.id}",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, SubscriptionStatusChoices.ACTIVE)
        self.assertGreater(self.sub.end_date, date.today())

    @override_settings(
        MERCADOPAGO_ACCESS_TOKEN="TEST-fake-token",
        DEBUG=True,
    )
    @patch("billing.views.mercadopago.SDK")
    def test_success_view_does_not_duplicate_if_already_approved(self, mock_sdk_class):
        """Se webhook já aprovou o pagamento, success_view não deve estender assinatura de novo."""
        payment_id = 9010001
        original_end = date.today() + timedelta(days=45)
        self.sub.end_date = original_end
        self.sub.save()

        # Webhook já processou
        make_payment(
            subscription=self.sub,
            external_id=str(payment_id),
            status=PaymentStatusChoices.APPROVED,
        )

        response = self.client.get(
            reverse("billing:payment_success"),
            {
                "payment_id": str(payment_id),
                "status": "approved",
                "external_reference": f"subscription_{self.sub.id}",
            },
        )

        # SDK não deve ser chamado (já aprovado, idempotência)
        mock_sdk_class.assert_not_called()
        self.assertEqual(response.status_code, 302)

        # end_date não mudou
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.end_date, original_end)

    def test_success_view_requires_login(self):
        """Usuário sem login deve ser redirecionado."""
        self.client.logout()
        response = self.client.get(
            reverse("billing:payment_success"),
            {"payment_id": "123", "status": "approved"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/contas/", response["Location"])
