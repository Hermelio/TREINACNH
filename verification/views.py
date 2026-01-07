"""
Views for verification app - Document upload with OCR processing.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from marketplace.models import InstructorProfile
from .models import InstructorDocument, AuditLog, DocumentTypeChoices
from .forms import DocumentUploadForm
from .services import DocumentVerificationService


@login_required
def document_upload_view(request):
    """Upload document for verification with OCR processing"""
    # Check if user is instructor
    if not request.user.profile.is_instructor:
        messages.error(request, 'Apenas instrutores podem enviar documentos.')
        return redirect('accounts:dashboard')
    
    # Get instructor profile
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
    except InstructorProfile.DoesNotExist:
        messages.error(request, 'Complete seu perfil de instrutor primeiro.')
        return redirect('marketplace:instructor_profile_edit')
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.instructor = instructor_profile
            document.save()
            
            # Process CNH documents with OCR
            if document.doc_type == DocumentTypeChoices.CNH:
                try:
                    service = DocumentVerificationService()
                    ocr_data = service.extract_cnh_data(document.file.path)
                    
                    # Save extracted data
                    document.extracted_cnh_number = ocr_data.get('cnh_number', '')
                    document.extracted_cpf = ocr_data.get('cpf', '')
                    document.extracted_name = ocr_data.get('name', '')
                    document.extracted_validity = ocr_data.get('validity_date')
                    document.ocr_confidence = ocr_data.get('confidence', 0)
                    
                    # Validate extracted data
                    if document.extracted_cnh_number:
                        document.cnh_valid = service.validate_cnh_number(document.extracted_cnh_number)
                    
                    if document.extracted_cpf:
                        document.cpf_valid = service.validate_cpf(document.extracted_cpf)
                    
                    if document.extracted_validity:
                        document.validity_ok = service.check_cnh_validity(document.extracted_validity)
                    
                    document.save()
                    
                    # Show detailed feedback
                    validation_msg = []
                    if document.cnh_valid:
                        validation_msg.append('✅ CNH válida')
                    else:
                        validation_msg.append('⚠️ Verifique o número da CNH')
                    
                    if document.cpf_valid:
                        validation_msg.append('✅ CPF válido')
                    else:
                        validation_msg.append('⚠️ Verifique o CPF')
                    
                    if document.validity_ok:
                        validation_msg.append('✅ Documento dentro da validade')
                    else:
                        validation_msg.append('⚠️ Documento pode estar vencido')
                    
                    messages.success(
                        request,
                        f'Documento enviado! OCR processado com {document.ocr_confidence}% de confiança. '
                        f'{" | ".join(validation_msg)}. Aguarde revisão do administrador.'
                    )
                    
                except Exception as e:
                    messages.warning(
                        request,
                        f'Documento enviado, mas houve erro no OCR: {str(e)}. '
                        f'Um administrador irá revisar manualmente.'
                    )
            else:
                messages.success(request, 'Documento enviado com sucesso! Aguarde a análise.')
            
            # Log action
            AuditLog.log(
                action='DOCUMENT_UPLOADED',
                object_type='InstructorDocument',
                object_id=document.pk,
                actor_user=request.user
            )
            
            return redirect('verification:my_documents')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'verification/document_upload.html', {'form': form})


@login_required
def my_documents_view(request):
    """View uploaded documents"""
    if not request.user.profile.is_instructor:
        messages.error(request, 'Apenas instrutores podem acessar esta página.')
        return redirect('accounts:dashboard')
    
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
        documents = InstructorDocument.objects.filter(instructor=instructor_profile).order_by('-uploaded_at')
    except InstructorProfile.DoesNotExist:
        documents = []
    
    context = {
        'documents': documents,
        'page_title': 'Meus Documentos',
    }
    return render(request, 'verification/my_documents.html', context)
