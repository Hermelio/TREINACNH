"""
Additional validators to prevent fraud and scams.
"""
import re
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from PIL import Image

# Optional: face recognition (requires dlib, cmake, face-recognition)
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False


class FraudPreventionValidator:
    """
    Advanced validators to prevent fraud, fake profiles, and scams.
    """
    
    @staticmethod
    def validate_selfie_with_document(selfie_path, document_path):
        """
        Compare selfie photo with document photo to verify identity.
        Uses face recognition to ensure it's the same person.
        
        Returns:
            dict: {
                'match': bool,
                'confidence': float,
                'message': str
            }
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return {
                'match': None,
                'confidence': 0,
                'message': 'Biblioteca face_recognition não instalada. Verificação manual necessária.'
            }
        
        try:
            # Load selfie image
            selfie_image = face_recognition.load_image_file(selfie_path)
            selfie_encodings = face_recognition.face_encodings(selfie_image)
            
            if not selfie_encodings:
                return {
                    'match': False,
                    'confidence': 0,
                    'message': 'Nenhum rosto detectado na selfie'
                }
            
            # Load document image
            document_image = face_recognition.load_image_file(document_path)
            document_encodings = face_recognition.face_encodings(document_image)
            
            if not document_encodings:
                return {
                    'match': False,
                    'confidence': 0,
                    'message': 'Nenhum rosto detectado no documento'
                }
            
            # Compare faces
            face_distances = face_recognition.face_distance(document_encodings, selfie_encodings[0])
            confidence = (1 - face_distances[0]) * 100  # Convert distance to percentage
            
            # Threshold: 60% confidence minimum
            match = confidence >= 60
            
            return {
                'match': match,
                'confidence': round(confidence, 2),
                'message': 'Identidade confirmada' if match else 'Rostos não correspondem'
            }
            
        except Exception as e:
            return {
                'match': False,
                'confidence': 0,
                'message': f'Erro na verificação: {str(e)}'
            }
    
    @staticmethod
    def validate_email_domain(email):
        """
        Validate email domain to detect disposable/temporary emails.
        """
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'temp-mail.org',
            'trashmail.com', 'yopmail.com', 'fakeinbox.com'
        ]
        
        domain = email.split('@')[-1].lower()
        
        if domain in disposable_domains:
            raise ValidationError(
                'Email temporário não é permitido. Use um email permanente.'
            )
        
        return True
    
    @staticmethod
    def validate_phone_carrier(phone_number):
        """
        Validate if phone number is from a real carrier (not VOIP).
        Requires integration with phone validation API like Twilio Lookup.
        """
        # TODO: Integrate with Twilio Lookup API or similar
        # For now, basic validation
        cleaned = re.sub(r'\D', '', phone_number)
        
        # Brazilian numbers must have 10-11 digits
        if len(cleaned) < 10 or len(cleaned) > 11:
            raise ValidationError('Número de telefone inválido')
        
        return True
    
    @staticmethod
    def check_duplicate_data(cpf=None, phone=None, email=None, user_id=None):
        """
        Check if CPF, phone or email is already registered by another user.
        Prevents multiple accounts with same data.
        """
        from accounts.models import Profile
        from django.contrib.auth.models import User
        
        duplicates = []
        
        if cpf:
            existing = Profile.objects.filter(cpf=cpf).exclude(user_id=user_id)
            if existing.exists():
                duplicates.append(f'CPF já cadastrado')
        
        if email:
            existing = User.objects.filter(email=email).exclude(id=user_id)
            if existing.exists():
                duplicates.append(f'Email já cadastrado')
        
        if phone:
            existing = Profile.objects.filter(phone=phone).exclude(user_id=user_id)
            if existing.exists():
                duplicates.append(f'Telefone já cadastrado')
        
        if duplicates:
            raise ValidationError(' | '.join(duplicates))
        
        return True
    
    @staticmethod
    def validate_bank_account_ownership(cpf, bank_account_cpf):
        """
        Verify that bank account belongs to the same CPF.
        Prevents money laundering and fake accounts.
        """
        # Remove formatting
        cpf_clean = re.sub(r'\D', '', cpf)
        bank_cpf_clean = re.sub(r'\D', '', bank_account_cpf)
        
        if cpf_clean != bank_cpf_clean:
            raise ValidationError(
                'A conta bancária deve estar no mesmo CPF do cadastro'
            )
        
        return True
    
    @staticmethod
    def check_suspicious_activity(user):
        """
        Check for suspicious activity patterns.
        """
        from verification.models import InstructorDocument
        from reviews.models import Review
        
        flags = []
        
        # Check multiple document rejections
        rejected_docs = InstructorDocument.objects.filter(
            instructor__user=user,
            status='REJECTED'
        ).count()
        
        if rejected_docs >= 3:
            flags.append('Múltiplos documentos rejeitados')
        
        # Check negative reviews
        if hasattr(user, 'instructor_profile'):
            negative_reviews = Review.objects.filter(
                instructor=user.instructor_profile,
                rating__lte=2
            ).count()
            
            if negative_reviews >= 5:
                flags.append('Múltiplas avaliações negativas')
        
        # Check account age vs activity
        account_age = (datetime.now().date() - user.date_joined.date()).days
        if account_age < 1:  # Less than 1 day old
            flags.append('Conta muito recente')
        
        return {
            'suspicious': len(flags) > 0,
            'flags': flags,
            'risk_level': 'high' if len(flags) >= 2 else 'medium' if len(flags) == 1 else 'low'
        }
    
    @staticmethod
    def validate_cnh_not_blacklisted(cnh_number):
        """
        Check if CNH is in blacklist (reported as stolen, fake, etc).
        """
        from .models import DocumentBlacklist
        
        blacklisted = DocumentBlacklist.objects.filter(
            document_type='CNH',
            document_number=cnh_number,
            is_active=True
        ).exists()
        
        if blacklisted:
            raise ValidationError(
                'Este documento foi reportado como inválido ou roubado'
            )
        
        return True
    
    @staticmethod
    def calculate_trust_score(user):
        """
        Calculate trust score based on multiple factors.
        Returns score from 0-100.
        """
        from verification.models import InstructorDocument
        from reviews.models import Review
        
        score = 50  # Base score
        
        # Email verified (+10)
        if user.email and user.profile.email_verified:
            score += 10
        
        # Phone verified (+10)
        if user.profile.phone and user.profile.phone_verified:
            score += 10
        
        # Document approved (+15)
        if hasattr(user, 'instructor_profile'):
            approved_docs = InstructorDocument.objects.filter(
                instructor=user.instructor_profile,
                status='APPROVED'
            ).count()
            score += min(approved_docs * 15, 15)
        
        # Positive reviews (+5 per review, max 15)
        if hasattr(user, 'instructor_profile'):
            positive_reviews = Review.objects.filter(
                instructor=user.instructor_profile,
                rating__gte=4
            ).count()
            score += min(positive_reviews * 5, 15)
        
        # Account age (+5 if > 30 days)
        account_age = (datetime.now().date() - user.date_joined.date()).days
        if account_age > 30:
            score += 5
        
        # Penalties
        # Rejected documents (-10 per rejection)
        if hasattr(user, 'instructor_profile'):
            rejected = InstructorDocument.objects.filter(
                instructor=user.instructor_profile,
                status='REJECTED'
            ).count()
            score -= rejected * 10
        
        # Negative reviews (-10 per bad review)
        if hasattr(user, 'instructor_profile'):
            negative = Review.objects.filter(
                instructor=user.instructor_profile,
                rating__lte=2
            ).count()
            score -= negative * 10
        
        # Keep score between 0-100
        return max(0, min(100, score))
