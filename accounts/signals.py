"""
Signals for accounts app - Handle trial activation on first login
"""
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from marketplace.models import InstructorProfile


@receiver(user_logged_in)
def activate_trial_on_first_login(sender, request, user, **kwargs):
    """
    Activate 14-day trial when verified instructor logs in for the first time.
    Also auto-creates InstructorProfile if the instructor doesn't have one yet.
    """
    try:
        profile = user.profile
        if not profile.is_instructor:
            return

        # Auto-create InstructorProfile if it doesn't exist
        # Use preferred_city if available, else skip (instructor will set when editing profile)
        if not InstructorProfile.objects.filter(user=user).exists():
            city = getattr(profile, 'preferred_city', None)
            if city:
                InstructorProfile.objects.create(
                    user=user,
                    city=city,
                    is_visible=False,
                    is_verified=False,
                )

        try:
            instructor_profile = InstructorProfile.objects.get(user=user)
        except InstructorProfile.DoesNotExist:
            return

        # Only activate trial if:
        # 1. Instructor is verified (documents approved)
        # 2. Trial hasn't been started yet
        # 3. No active subscription
        if (instructor_profile.is_verified and
            not instructor_profile.trial_start_date and
            not instructor_profile.has_active_subscription()):

            instructor_profile.activate_trial()

            from django.contrib import messages
            messages.success(
                request,
                '🎉 Bem-vindo! Seu período de teste gratuito de 14 dias foi ativado. '
                'Você pode receber contatos de alunos durante este período.'
            )

    except (AttributeError, Exception):
        pass
