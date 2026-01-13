"""
Django management command to check expiring subscriptions and send email reminders.
Run daily via cron: 0 9 * * * cd /var/www/TREINACNH && venv/bin/python manage.py check_expiring_subscriptions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from billing.models import Subscription, SubscriptionStatusChoices


class Command(BaseCommand):
    help = 'Check for expiring subscriptions and send email reminders'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Check subscriptions expiring in 3 days
        warning_date = today + timedelta(days=3)
        
        expiring_subscriptions = Subscription.objects.filter(
            status=SubscriptionStatusChoices.ACTIVE,
            end_date=warning_date
        ).select_related('instructor__user', 'plan')
        
        self.stdout.write(self.style.WARNING(f'Checking subscriptions expiring on {warning_date}...'))
        
        for sub in expiring_subscriptions:
            instructor = sub.instructor
            user = instructor.user
            
            self.stdout.write(f'  - {user.get_full_name()} ({user.email}) - {sub.plan.name}')
            
            # TODO: Send email
            # send_expiration_warning_email(
            #     to_email=user.email,
            #     instructor_name=user.get_full_name(),
            #     plan_name=sub.plan.name,
            #     expiration_date=sub.end_date,
            #     renewal_url=f"{settings.SITE_URL}/planos/checkout/{sub.id}/"
            # )
        
        # Check already expired subscriptions
        expired_subscriptions = Subscription.objects.filter(
            status=SubscriptionStatusChoices.ACTIVE,
            end_date__lt=today
        ).select_related('instructor__user', 'plan')
        
        if expired_subscriptions.exists():
            self.stdout.write(self.style.ERROR(f'\nFound {expired_subscriptions.count()} expired subscriptions:'))
            
            for sub in expired_subscriptions:
                user = sub.instructor.user
                self.stdout.write(f'  - {user.get_full_name()} - Expired on {sub.end_date}')
                
                # TODO: Auto-pause or send urgent reminder
                # sub.status = SubscriptionStatusChoices.PAUSED
                # sub.save()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Check complete'))
        self.stdout.write(f'  Expiring in 3 days: {expiring_subscriptions.count()}')
        self.stdout.write(f'  Already expired: {expired_subscriptions.count()}')
