"""
Management command to check status of pending payments in Mercado Pago.
Useful for recovering payments that webhook may have missed.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from billing.models import Payment, PaymentStatusChoices, SubscriptionStatusChoices
from datetime import timedelta
import mercadopago
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check status of pending payments and update if approved'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Check payments from the last N days (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Check if Mercado Pago is configured
        if not settings.MERCADOPAGO_ACCESS_TOKEN:
            self.stdout.write(self.style.ERROR('Mercado Pago not configured'))
            return
        
        # Find pending payments from last N days
        cutoff_date = timezone.now() - timedelta(days=days)
        pending_payments = Payment.objects.filter(
            status=PaymentStatusChoices.PENDING,
            created_at__gte=cutoff_date
        ).select_related('subscription', 'subscription__instructor', 'subscription__plan')
        
        count = pending_payments.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS(f'No pending payments in the last {days} days'))
            return
        
        self.stdout.write(f'Found {count} pending payment(s) to check')
        
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        updated = 0
        approved = 0
        
        for payment in pending_payments:
            try:
                # Query Mercado Pago for current status
                payment_info = sdk.payment().get(payment.external_id)
                
                if payment_info.get("status") != 200:
                    self.stdout.write(
                        self.style.WARNING(f'  - Could not fetch payment {payment.external_id}')
                    )
                    continue
                
                payment_data = payment_info["response"]
                mp_status = payment_data.get('status', 'pending')
                
                if mp_status != 'pending':
                    self.stdout.write(
                        f'  - Payment {payment.external_id}: {mp_status} '
                        f'(Subscription: {payment.subscription.id})'
                    )
                    
                    if not dry_run:
                        # Update payment status
                        status_map = {
                            'approved': PaymentStatusChoices.APPROVED,
                            'authorized': PaymentStatusChoices.APPROVED,
                            'rejected': PaymentStatusChoices.REJECTED,
                            'cancelled': PaymentStatusChoices.CANCELLED,
                            'refunded': PaymentStatusChoices.REFUNDED,
                        }
                        
                        new_status = status_map.get(mp_status, PaymentStatusChoices.PENDING)
                        payment.status = new_status
                        payment.payment_details = payment_data
                        
                        if new_status == PaymentStatusChoices.APPROVED:
                            payment.paid_at = timezone.now()
                            
                            # Extend subscription
                            subscription = payment.subscription
                            if subscription.end_date and subscription.end_date >= timezone.now().date():
                                new_end_date = subscription.end_date + timedelta(days=30)
                            else:
                                new_end_date = timezone.now().date() + timedelta(days=30)
                            
                            subscription.end_date = new_end_date
                            subscription.status = SubscriptionStatusChoices.ACTIVE
                            subscription.save()
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'    Extended subscription to {new_end_date}'
                                )
                            )
                            approved += 1
                        
                        payment.save()
                        updated += 1
                        logger.info(f'Updated payment {payment.external_id} to {new_status}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  - Error checking payment {payment.external_id}: {str(e)}')
                )
                logger.error(f'Error checking payment {payment.external_id}: {str(e)}')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nUpdated {updated} payment(s), {approved} approved and extended'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\nWould update {updated} payment(s) (dry run)')
            )
