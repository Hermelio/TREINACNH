"""
Signals for marketplace app.
Handles automatic notifications when instructors register.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import InstructorProfile, StudentLead


@receiver(post_save, sender=InstructorProfile)
def notify_students_in_state(sender, instance, created, **kwargs):
    """
    When a new instructor is created and verified, notify students in the same state.
    """
    # Only process if instructor is verified and visible
    if not instance.is_verified or not instance.is_visible:
        return
    
    # Get the state from the instructor's city
    state = instance.city.state
    
    # Find all students in the same state who haven't been notified yet
    students_to_notify = StudentLead.objects.filter(
        state=state,
        notified_about_instructor=False
    )
    
    # Mark them as having an instructor available
    # The actual notification (WhatsApp/Email) should be done manually or via a task
    count = students_to_notify.update(
        notified_about_instructor=True,
        notified_at=timezone.now()
    )
    
    if count > 0 and created:
        # Log for admin visibility
        print(f"✓ {count} alunos em {state.code} foram marcados para notificação sobre novo instrutor")


@receiver(post_save, sender=InstructorProfile)
def log_instructor_status_change(sender, instance, created, **kwargs):
    """
    Log when instructor verification status changes.
    """
    if created:
        print(f"Novo instrutor cadastrado: {instance.user.get_full_name()} em {instance.city}/{instance.city.state.code}")
    elif instance.is_verified:
        # Check if there are students waiting in this state
        student_count = StudentLead.objects.filter(
            state=instance.city.state,
            notified_about_instructor=False
        ).count()
        
        if student_count > 0:
            print(f"⚠️ ATENÇÃO: {student_count} alunos aguardando em {instance.city.state.code} podem ser notificados!")
