"""
Management command to validate and update subscription statuses.
Run this daily via cron job.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from billing.models import Subscription, SubscriptionStatusChoices
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate and update subscription statuses (pause expired ones)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        today = date.today()
        
        # Find expired active subscriptions
        expired_subscriptions = Subscription.objects.filter(
            status=SubscriptionStatusChoices.ACTIVE,
            end_date__lt=today
        ).select_related('instructor', 'plan')
        
        count = expired_subscriptions.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired subscriptions found'))
            return
        
        self.stdout.write(f'Found {count} expired subscription(s)')
        
        for subscription in expired_subscriptions:
            self.stdout.write(
                f'  - {subscription.instructor.user.get_full_name()} '
                f'({subscription.plan.name}) - Expired: {subscription.end_date}'
            )
            
            if not dry_run:
                subscription.status = SubscriptionStatusChoices.PAUSED
                subscription.save()
                logger.info(f'Paused expired subscription {subscription.id}')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully paused {count} expired subscription(s)')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Would pause {count} subscription(s) (dry run)')
            )
