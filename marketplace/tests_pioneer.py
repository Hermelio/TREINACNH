"""
Tests for the Instrutor Pioneiro benefit.

Casos cobertos:
1. Instrutor da lista → recebe badge + plano ativo por 60 dias.
2. Instrutor fora da lista → NÃO recebe nada.
3. Após expiração → volta ao fluxo normal do plano pago.
4. Idempotência: rodar o comando duas vezes não duplica nem reduz o prazo.
5. can_receive_leads() respeita o benefício pioneiro.
6. badges property inclui a badge de pioneiro somente para is_pioneer=True.
"""
from datetime import timedelta, date

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from io import StringIO

from marketplace.models import InstructorProfile, State, City
from marketplace.management.commands.activate_pioneers import (
    Command as ActivateCommand,
    PIONEER_NAMES,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_instructor(first_name: str, last_name: str, city) -> InstructorProfile:
    username = f"{first_name.lower().replace(' ', '_')}_{last_name.lower().replace(' ', '_')}"[:150]
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'first_name': first_name, 'last_name': last_name},
    )
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    profile, _ = InstructorProfile.objects.get_or_create(
        user=user,
        defaults={
            'city': city,
            'is_visible': True,
            'is_verified': True,
        },
    )
    return profile


def _run_command(apply: bool = False) -> str:
    """Run activate_pioneers command and return stdout."""
    out = StringIO()
    cmd = ActivateCommand()
    cmd.stdout = out
    cmd.style = ActivateCommand().style  # type: ignore[attr-defined]
    from django.test.utils import override_settings  # noqa
    cmd.execute(apply=apply, no_color=True, verbosity=1, pythonpath=None, settings=None, traceback=False)
    return out.getvalue()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class PioneerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        state = State.objects.create(code='SP', name='São Paulo')
        cls.city = City.objects.create(state=state, name='Teste', slug='teste-sp')

    # --- is_pioneer_active ----------------------------------------------------

    def test_pioneer_active_when_date_in_future(self):
        p = _create_instructor('Test', 'Pioneer', self.city)
        p.is_pioneer = True
        p.pioneer_free_until = timezone.now().date() + timedelta(days=30)
        p.save()
        self.assertTrue(p.is_pioneer_active())

    def test_pioneer_inactive_when_date_past(self):
        p = _create_instructor('Test', 'Expired', self.city)
        p.is_pioneer = True
        p.pioneer_free_until = timezone.now().date() - timedelta(days=1)
        p.save()
        self.assertFalse(p.is_pioneer_active())

    def test_pioneer_inactive_when_flag_false(self):
        p = _create_instructor('Test', 'NotPioneer', self.city)
        p.is_pioneer = False
        p.pioneer_free_until = timezone.now().date() + timedelta(days=30)
        p.save()
        self.assertFalse(p.is_pioneer_active())

    def test_pioneer_inactive_when_no_date(self):
        p = _create_instructor('Test', 'NoDate', self.city)
        p.is_pioneer = True
        p.pioneer_free_until = None
        p.save()
        self.assertFalse(p.is_pioneer_active())

    # --- can_receive_leads ----------------------------------------------------

    def test_pioneer_can_receive_leads(self):
        """Instrutor pioneiro com prazo válido pode receber leads."""
        p = _create_instructor('Active', 'Pioneer', self.city)
        p.is_pioneer = True
        p.pioneer_free_until = timezone.now().date() + timedelta(days=60)
        p.save()
        self.assertTrue(p.can_receive_leads())

    def test_expired_pioneer_cannot_receive_leads_without_subscription(self):
        """Pioneiro expirado sem assinatura volta ao fluxo normal (sem acesso)."""
        p = _create_instructor('Expired', 'Pioneer', self.city)
        p.is_pioneer = True
        p.pioneer_free_until = timezone.now().date() - timedelta(days=1)
        p.is_trial_active = False
        p.save()
        self.assertFalse(p.can_receive_leads())

    def test_non_pioneer_default_no_access(self):
        """Instrutor sem trial, sem assinatura, sem pioneer não pode receber leads."""
        p = _create_instructor('Normal', 'Instructor', self.city)
        p.is_pioneer = False
        p.is_trial_active = False
        p.save()
        self.assertFalse(p.can_receive_leads())

    # --- badges ---------------------------------------------------------------

    def test_pioneer_badge_appears_for_pioneer(self):
        p = _create_instructor('Badge', 'Pioneer', self.city)
        p.is_pioneer = True
        p.is_verified = True
        # set created_at far in past to avoid "Novo" badge
        InstructorProfile.objects.filter(pk=p.pk).update(
            created_at=timezone.now() - timedelta(days=40)
        )
        p.refresh_from_db()
        names = [b['name'] for b in p.badges]
        self.assertIn('Verificado', names)
        self.assertIn('Instrutor Pioneiro', names)

    def test_pioneer_badge_absent_for_non_pioneer(self):
        p = _create_instructor('Normal', 'NoBadge', self.city)
        p.is_pioneer = False
        p.is_verified = True
        InstructorProfile.objects.filter(pk=p.pk).update(
            created_at=timezone.now() - timedelta(days=40)
        )
        p.refresh_from_db()
        names = [b['name'] for b in p.badges]
        self.assertNotIn('Instrutor Pioneiro', names)

    # --- get_access_status ----------------------------------------------------

    def test_access_status_pioneer_active(self):
        p = _create_instructor('Status', 'Pioneer', self.city)
        p.is_pioneer = True
        p.pioneer_free_until = timezone.now().date() + timedelta(days=45)
        p.save()
        status = p.get_access_status()
        self.assertTrue(status['can_receive_leads'])
        self.assertEqual(status['reason'], 'pioneer_active')
        self.assertTrue(status['is_pioneer'])
        self.assertGreater(status['days_remaining'], 0)


class ActivatePioneerCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        state = State.objects.create(code='RJ', name='Rio de Janeiro')
        cls.city = City.objects.create(state=state, name='Rio', slug='rio-rj')

    def _run(self, apply=False) -> str:
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command('activate_pioneers', apply=apply, stdout=out, no_color=True)
        return out.getvalue()

    def test_dry_run_does_not_save(self):
        """dry-run não deve persistir nada."""
        # Create one pioneer from the list
        first, *rest_parts = PIONEER_NAMES[0].split()
        last = ' '.join(rest_parts)
        p = _create_instructor(first, last, self.city)

        output = self._run(apply=False)

        p.refresh_from_db()
        self.assertFalse(p.is_pioneer)
        self.assertIsNone(p.pioneer_free_until)
        self.assertIn('DRY-RUN', output.upper())

    def test_apply_activates_pioneer(self):
        """--apply deve setar is_pioneer=True e pioneer_free_until=+60 dias."""
        first, *rest_parts = PIONEER_NAMES[0].split()
        last = ' '.join(rest_parts)
        p = _create_instructor(first, last, self.city)

        self._run(apply=True)

        p.refresh_from_db()
        self.assertTrue(p.is_pioneer)
        self.assertIsNotNone(p.pioneer_free_until)
        expected = timezone.now().date() + timedelta(days=60)
        self.assertEqual(p.pioneer_free_until, expected)

    def test_outsider_not_activated(self):
        """Instrutor fora da lista NÃO deve ser ativado."""
        p = _create_instructor('Carlos', 'Outsider Da Silva', self.city)

        self._run(apply=True)

        p.refresh_from_db()
        self.assertFalse(p.is_pioneer)
        self.assertIsNone(p.pioneer_free_until)

    def test_idempotent_does_not_reduce_date(self):
        """Rodar o comando novamente não deve reduzir pioneer_free_until já maior."""
        first, *rest_parts = PIONEER_NAMES[0].split()
        last = ' '.join(rest_parts)
        p = _create_instructor(first, last, self.city)
        future_date = timezone.now().date() + timedelta(days=200)
        p.is_pioneer = True
        p.pioneer_free_until = future_date
        p.save()

        self._run(apply=True)

        p.refresh_from_db()
        self.assertEqual(p.pioneer_free_until, future_date, "A data maior não deve ser reduzida")

    def test_warns_when_name_not_found(self):
        """Deve avisar no log se algum nome da lista não estiver no banco."""
        # No instructors created → all names are missing
        output = self._run(apply=False)
        self.assertIn('não encontrados', output.lower())
