"""
Views for reviews app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from marketplace.models import InstructorProfile
from .models import Review, Report
from .forms import ReviewForm, ReportForm


@require_http_methods(["GET", "POST"])
def review_create_view(request, instructor_pk):
    """Create a review for an instructor"""
    instructor = get_object_or_404(InstructorProfile, pk=instructor_pk, is_visible=True)
    
    # Check if user already reviewed this instructor
    if request.user.is_authenticated:
        existing_review = Review.objects.filter(instructor=instructor, author_user=request.user).first()
        if existing_review:
            messages.warning(request, 'Você já avaliou este instrutor.')
            return redirect('marketplace:instructor_detail', pk=instructor.pk)
        
        # Check if user has completed lessons with this instructor
        from marketplace.models import Lead, LeadStatusChoices
        has_completed_lessons = Lead.objects.filter(
            student_user=request.user,
            instructor=instructor,
            status=LeadStatusChoices.COMPLETED
        ).exists()
        
        if not has_completed_lessons:
            messages.error(
                request,
                'Você só pode avaliar este instrutor após finalizar aulas com ele. '
                'Entre em contato com o instrutor e solicite que ele marque suas aulas como finalizadas.'
            )
            return redirect('marketplace:instructor_detail', pk=instructor.pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.instructor = instructor
            
            if request.user.is_authenticated:
                review.author_user = request.user
            else:
                review.author_name = 'Aluno'
            
            # Save IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                review.ip_address = x_forwarded_for.split(',')[0]
            else:
                review.ip_address = request.META.get('REMOTE_ADDR')
            
            try:
                review.save()
                messages.success(request, 'Avaliação enviada com sucesso! Ela será publicada após moderação.')
                return redirect('marketplace:instructor_detail', pk=instructor.pk)
            except Exception as e:
                messages.error(request, f'Erro ao salvar avaliação: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ReviewForm(user=request.user)
    
    context = {
        'form': form,
        'instructor': instructor,
        'page_title': f'Avaliar {instructor.user.get_full_name()}',
    }
    return render(request, 'reviews/review_create.html', context)


@require_http_methods(["GET", "POST"])
def report_create_view(request, instructor_pk):
    """Create a report about an instructor"""
    instructor = get_object_or_404(InstructorProfile, pk=instructor_pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.instructor = instructor
            
            if request.user.is_authenticated:
                report.reporter_user = request.user
            
            # Save IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                report.ip_address = x_forwarded_for.split(',')[0]
            else:
                report.ip_address = request.META.get('REMOTE_ADDR')
            
            report.save()
            
            messages.success(request, 'Denúncia enviada com sucesso. Nossa equipe irá analisá-la.')
            return redirect('marketplace:instructor_detail', pk=instructor.pk)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ReportForm(user=request.user)
    
    context = {
        'form': form,
        'instructor': instructor,
        'page_title': f'Denunciar {instructor.user.get_full_name()}',
    }
    return render(request, 'reviews/report_create.html', context)
