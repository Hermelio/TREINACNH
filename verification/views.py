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
    """Upload document for verification - DISABLED - Admin handles verification"""
    # Check if user is instructor
    if not request.user.profile.is_instructor:
        messages.error(request, 'Apenas instrutores podem acessar esta página.')
        return redirect('accounts:dashboard')
    
    # Redirect to my_documents with info message
    messages.info(
        request,
        'A verificação de documentos agora é realizada pela nossa equipe administrativa. '
        'Não é necessário enviar documentos. Nossa equipe entrará em contato via CPF cadastrado.'
    )
    return redirect('verification:my_documents')


@login_required
def my_documents_view(request):
    """View uploaded documents"""
    if not request.user.profile.is_instructor:
        messages.error(request, 'Apenas instrutores podem acessar esta página.')
        return redirect('accounts:dashboard')
    
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
        documents = InstructorDocument.objects.filter(
            instructor=instructor_profile
        ).order_by('-uploaded_at')
    except InstructorProfile.DoesNotExist:
        documents = []
        instructor_profile = None

    docs_by_type = {d.doc_type: d for d in documents}
    cnh_doc  = docs_by_type.get(DocumentTypeChoices.CNH)
    cert_doc = docs_by_type.get(DocumentTypeChoices.CERT_INSTRUTOR)

    def _can_upload(doc):
        return doc is None or doc.status == 'REJECTED'

    context = {
        'documents': documents,
        'cnh_doc':   cnh_doc,
        'cert_doc':  cert_doc,
        'can_upload_cnh':  _can_upload(cnh_doc),
        'can_upload_cert': _can_upload(cert_doc),
        'is_verified': instructor_profile.is_verified if instructor_profile else False,
        'page_title': 'Meus Documentos',
    }
    return render(request, 'verification/my_documents.html', context)


@login_required
def document_status_api(request):
    """API endpoint to get document status for instructors"""
    from django.http import JsonResponse
    
    if not request.user.profile.is_instructor:
        return JsonResponse({'error': 'Apenas instrutores'}, status=403)
    
    try:
        instructor_profile = InstructorProfile.objects.get(user=request.user)
        documents = InstructorDocument.objects.filter(instructor=instructor_profile)
    except InstructorProfile.DoesNotExist:
        return JsonResponse({'error': 'Perfil de instrutor não encontrado'}, status=404)
    
    docs_by_type = {d.doc_type: d for d in documents}
    cnh_doc = docs_by_type.get(DocumentTypeChoices.CNH)
    cert_doc = docs_by_type.get(DocumentTypeChoices.CERT_INSTRUTOR)
    
    def get_doc_info(doc, doc_name):
        if not doc:
            return {
                'status': 'NOT_SENT',
                'status_display': 'Não enviado',
                'badge_class': 'secondary',
                'notes': None
            }
        
        badge_classes = {
            'PENDING': 'warning',
            'APPROVED': 'success',
            'REJECTED': 'danger',
        }
        
        status_displays = {
            'PENDING': 'Em análise',
            'APPROVED': 'Aprovado',
            'REJECTED': 'Rejeitado',
        }
        
        return {
            'status': doc.status,
            'status_display': status_displays.get(doc.status, doc.get_status_display()),
            'badge_class': badge_classes.get(doc.status, 'secondary'),
            'notes': doc.notes if doc.status == 'REJECTED' else None
        }
    
    # Check statuses
    cnh_info = get_doc_info(cnh_doc, 'CNH')
    cert_info = get_doc_info(cert_doc, 'Certificado')
    
    missing_docs = []
    if cnh_info['status'] == 'NOT_SENT':
        missing_docs.append('CNH')
    if cert_info['status'] == 'NOT_SENT':
        missing_docs.append('Certificado')
    
    has_rejected = (
        (cnh_doc and cnh_doc.status == 'REJECTED') or
        (cert_doc and cert_doc.status == 'REJECTED')
    )
    
    all_pending = (
        (cnh_doc and cnh_doc.status == 'PENDING' and cert_doc and cert_doc.status == 'PENDING') or
        (cnh_doc and cnh_doc.status == 'PENDING' and not cert_doc) or
        (cert_doc and cert_doc.status == 'PENDING' and not cnh_doc)
    )
    
    return JsonResponse({
        'is_verified': instructor_profile.is_verified,
        'cnh': cnh_info,
        'cert': cert_info,
        'missing_docs': missing_docs,
        'has_rejected': has_rejected,
        'all_pending': all_pending,
    })
