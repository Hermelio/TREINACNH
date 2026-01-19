"""
Custom adapters for django-allauth to integrate with our Profile system.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle social account signup.
    Creates Profile automatically when user signs up via Google.
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
            # Get first name and last name
            first_name = data.get('given_name', '')
            last_name = data.get('family_name', '')
            
            user.first_name = first_name
            user.last_name = last_name
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save user and create Profile.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Profile is created automatically by signal in accounts/models.py
        # But we ensure it exists
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        if created:
            # Set default role based on request parameter or context
            # By default, Google login users are students (not instructors)
            profile.is_instructor = False
            profile.save()
        
        return user
