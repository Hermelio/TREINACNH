"""
Service for document verification and OCR extraction.
"""
import os
import re
from datetime import datetime
from PIL import Image
import pytesseract

# Optional dependencies for advanced features
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


class DocumentVerificationService:
    """
    Service to handle document verification for instructors.
    Includes OCR extraction and data validation.
    """
    
    @staticmethod
    def preprocess_image(image_path):
        """
        Preprocess image to improve OCR accuracy.
        Requires opencv-python (cv2).
        """
        if not CV2_AVAILABLE:
            # Return original image if cv2 not available
            return Image.open(image_path)
        
        # Read image
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        return Image.fromarray(thresh)
    
    @staticmethod
    def extract_cnh_data(image_path):
        """
        Extract data from CNH (driver's license) using OCR.
        Returns dict with extracted information.
        """
        try:
            # Preprocess image for better OCR
            try:
                processed_image = DocumentVerificationService.preprocess_image(image_path)
            except Exception as e:
                print(f"Preprocessing failed, using original: {e}")
                processed_image = Image.open(image_path)
            
            # Perform OCR with Portuguese language
            text = pytesseract.image_to_string(processed_image, lang='por')
            
            # Calculate confidence (simple heuristic based on patterns found)
            confidence = 0
            patterns_found = 0
            
            # Extract CNH number (11 digits)
            cnh_match = re.search(r'\b\d{11}\b', text)
            cnh_number = cnh_match.group(0) if cnh_match else None
            if cnh_number:
                patterns_found += 1
            
            # Extract CPF (11 digits with or without formatting)
            cpf_match = re.search(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', text)
            cpf = cpf_match.group(0).replace('.', '').replace('-', '') if cpf_match else None
            if cpf:
                patterns_found += 1
            
            # Extract name (usually in uppercase after "Nome" label)
            name_match = re.search(r'(?:Nome|NOME)[:\s]+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+)', text, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else None
            if name:
                patterns_found += 1
            
            # Extract validity date (DD/MM/YYYY format)
            validity_match = re.search(r'(?:Validade|VAL|Valid)[:\s]*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
            validity_str = validity_match.group(1) if validity_match else None
            validity_date = None
            
            if validity_str:
                try:
                    validity_date = datetime.strptime(validity_str, '%d/%m/%Y').date()
                    patterns_found += 1
                except ValueError:
                    pass
            
            # Calculate confidence percentage (0-100%)
            confidence = min(100, (patterns_found / 4) * 100)  # 4 key fields
            
            return {
                'success': True,
                'cnh_number': cnh_number,
                'cpf': cpf,
                'name': name,
                'validity_date': validity_date,
                'confidence': round(confidence, 2),
                'raw_text': text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_cnh_number(cnh_number):
        """
        Validate CNH number using check digit algorithm.
        Returns True if valid.
        """
        if not cnh_number or len(cnh_number) != 11:
            return False
        
        try:
            # Remove non-numeric characters
            cnh = re.sub(r'\D', '', cnh_number)
            
            # Check if all digits are the same
            if len(set(cnh)) == 1:
                return False
            
            # Calculate first check digit
            sum1 = 0
            for i, digit in enumerate(cnh[:9], start=9):
                sum1 += int(digit) * i
            
            dv1 = sum1 % 11
            if dv1 >= 10:
                dv1 = 0
            
            # Calculate second check digit
            sum2 = 0
            for i, digit in enumerate(cnh[:9], start=1):
                sum2 += int(digit) * i
            
            dv2 = sum2 % 11
            if dv2 >= 10:
                dv2 = 0
            
            # Validate
            return int(cnh[9]) == dv1 and int(cnh[10]) == dv2
            
        except Exception:
            return False
    
    @staticmethod
    def validate_cpf(cpf):
        """
        Validate CPF number.
        Returns True if valid.
        """
        # Remove formatting
        cpf = re.sub(r'\D', '', cpf)
        
        if len(cpf) != 11 or len(set(cpf)) == 1:
            return False
        
        # Calculate first digit
        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = 11 - (sum1 % 11)
        if digit1 >= 10:
            digit1 = 0
        
        # Calculate second digit
        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = 11 - (sum2 % 11)
        if digit2 >= 10:
            digit2 = 0
        
        return int(cpf[9]) == digit1 and int(cpf[10]) == digit2
    
    @staticmethod
    def check_cnh_validity(validity_date_str):
        """
        Check if CNH is still valid.
        Returns dict with status and days remaining.
        """
        try:
            validity_date = datetime.strptime(validity_date_str, '%d/%m/%Y')
            today = datetime.now()
            
            days_remaining = (validity_date - today).days
            
            return {
                'is_valid': days_remaining > 0,
                'days_remaining': days_remaining,
                'validity_date': validity_date
            }
        except Exception:
            return {
                'is_valid': False,
                'error': 'Invalid date format'
            }
    
    @staticmethod
    def prepare_serpro_integration_data(instructor_profile):
        """
        Prepare data for future integration with Serpro API.
        Serpro is the official government API for document validation.
        
        API Documentation: https://www.serpro.gov.br/
        Note: Requires paid subscription and government authorization.
        """
        return {
            'cpf': instructor_profile.user.profile.cpf if hasattr(instructor_profile.user.profile, 'cpf') else None,
            'cnh_number': instructor_profile.cnh_number if hasattr(instructor_profile, 'cnh_number') else None,
            'full_name': instructor_profile.user.get_full_name(),
            'birth_date': instructor_profile.birth_date if hasattr(instructor_profile, 'birth_date') else None,
            # Future integration endpoint
            'api_endpoint': 'https://gateway.apiserpro.serpro.gov.br/consulta-cnh/v1/cnh/{cnh}',
            'requires_oauth': True,
            'documentation': 'https://www.serpro.gov.br/menu/nosso-portfolio/por-publico/para-quem-ja-e-cliente/servicos-ao-cidadao-1/consulta-cnh'
        }
