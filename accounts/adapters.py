"""
Custom adapters for django-allauth to integrate with our Profile system.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.urls import reverse


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle social account signup.
    Creates Profile automatically when user signs up via Google.
    New users are marked is_profile_complete=False so they must choose
    Aluno/Instrutor before using the site.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Called before social login/signup.
        Links existing email accounts.
        """
        # If user exists with this email, connect the account
        if sociallogin.is_existing:
            return

        # Check if email already exists
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
            from django.contrib.auth import get_user_model
            User = get_user_model()

            try:
                user = User.objects.get(email=email)
                # Connect this social account to existing user
                sociallogin.connect(request, user)
                messages.info(request, 'Sua conta Google foi conectada com sucesso!')
            except User.DoesNotExist:
                pass

    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social account.
        """
        user = super().populate_user(request, sociallogin, data)

        # Get data from Google
        if sociallogin.account.provider == 'google':
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save user and create Profile.
        New profiles (first Google login) are marked as incomplete
        so the user must choose Aluno/Instrutor.
        """
        user = super().save_user(request, sociallogin, form)

        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)

        if created:
            # Force user to choose their role before using the site
            profile.is_profile_complete = False
            profile.save()

        return user

    def get_login_redirect_url(self, request):
        """
        After Google login, send incomplete profiles to the role-selection page.
        """
        profile = getattr(request.user, 'profile', None)
        if profile and not profile.is_profile_complete:
            return reverse('accounts:complete_profile')
        return super().get_login_redirect_url(request)
