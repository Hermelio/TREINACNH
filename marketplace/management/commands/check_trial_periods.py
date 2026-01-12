"""
Management command to check trial periods and send expiration notifications.
Should be run daily via cron job.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from marketplace.models import InstructorProfile


class Command(BaseCommand):
    help = 'Check trial periods and send expiration notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Get all instructors with active trial
        instructors = InstructorProfile.objects.filter(
            is_trial_active=True,
            trial_end_date__isnull=False
        )
        
        notifications_sent = 0
        profiles_blocked = 0
        
        for instructor in instructors:
            days_remaining = (instructor.trial_end_date - now).days
            
            # Trial expired - block profile
            if now >= instructor.trial_end_date:
                if not instructor.trial_blocked_notified:
                    self.send_trial_expired_email(instructor)
                    instructor.trial_blocked_notified = True
                    instructor.is_visible = False
                    instructor.is_trial_active = False
                    instructor.save()
                    profiles_blocked += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Blocked: {instructor.user.get_full_name()} - Trial expired'
                        )
                    )
            
            # 7 days before expiration
            elif days_remaining == 7 and not instructor.trial_expiration_notified_7d:
                self.send_trial_warning_email(instructor, days_remaining)
                instructor.trial_expiration_notified_7d = True
                instructor.save()
                notifications_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Notified (7d): {instructor.user.get_full_name()}'
                    )
                )
            
            # 3 days before expiration
            elif days_remaining == 3 and not instructor.trial_expiration_notified_3d:
                self.send_trial_warning_email(instructor, days_remaining)
                instructor.trial_expiration_notified_3d = True
                instructor.save()
                notifications_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Notified (3d): {instructor.user.get_full_name()}'
                    )
                )
            
            # 1 day before expiration
            elif days_remaining == 1 and not instructor.trial_expiration_notified_1d:
                self.send_trial_warning_email(instructor, days_remaining)
                instructor.trial_expiration_notified_1d = True
                instructor.save()
                notifications_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Notified (1d): {instructor.user.get_full_name()}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Trial check completed:'
                f'\n  - {notifications_sent} notifications sent'
                f'\n  - {profiles_blocked} profiles blocked'
            )
        )
    
    def send_trial_warning_email(self, instructor, days_remaining):
        """Send warning email before trial expiration"""
        subject = f'⚠️ Seu período de teste expira em {days_remaining} {"dia" if days_remaining == 1 else "dias"}!'
        
        context = {
            'instructor': instructor,
            'days_remaining': days_remaining,
            'trial_end_date': instructor.trial_end_date,
        }
        
        message = f'''
Olá {instructor.user.first_name},

Seu período de teste gratuito no TreinaCNH está chegando ao fim!

⏰ Restam apenas {days_remaining} {"dia" if days_remaining == 1 else "dias"} até {instructor.trial_end_date.strftime("%d/%m/%Y")}

O que acontece após o período de teste?
• Seu perfil será pausado automaticamente
• Você não receberá mais solicitações de alunos
• Para continuar ativo, será necessário assinar um plano

💡 Não perca seus alunos!
Escolha um plano agora e continue recebendo solicitações:
http://72.61.36.89:8080/planos/

Dúvidas? Fale conosco pelo WhatsApp.

Atenciosamente,
Equipe TreinaCNH
'''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instructor.user.email],
                fail_silently=False,
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending email to {instructor.user.email}: {str(e)}')
            )
    
    def send_trial_expired_email(self, instructor):
        """Send email when trial has expired and profile is blocked"""
        subject = '🔒 Seu período de teste expirou - Perfil pausado'
        
        message = f'''
Olá {instructor.user.first_name},

Seu período de teste gratuito no TreinaCNH expirou.

🔒 Seu perfil foi pausado automaticamente
Você não está mais visível para novos alunos na plataforma.

Para reativar seu perfil e continuar recebendo solicitações de alunos, 
escolha um de nossos planos:

👉 Acesse: http://72.61.36.89:8080/planos/

📊 Benefícios de assinar:
• Perfil sempre ativo
• Receba solicitações ilimitadas
• Suporte prioritário
• Sem compromisso (cancele quando quiser)

Ficou com dúvidas? Estamos aqui para ajudar!
WhatsApp: [seu número]
E-mail: contato@treinacnh.com

Atenciosamente,
Equipe TreinaCNH
'''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instructor.user.email],
                fail_silently=False,
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending email to {instructor.user.email}: {str(e)}')
            )
