"""
Views for authentication and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django_ratelimit.decorators import ratelimit
from .forms import UserRegistrationForm, CustomLoginForm, ProfileEditForm, CompleteProfileForm, StudentDataForm
from .models import Profile, RoleChoices


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def register_view(request):
    """
    User registration view.
    Creates a new user and profile, then logs them in.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Registration form already captured role — mark profile complete
            user.profile.is_profile_complete = True

            # Process instructor extra fields if provided
            if user.profile.is_instructor:
                whatsapp = request.POST.get('whatsapp', '').strip()
                if whatsapp:
                    user.profile.whatsapp_number = whatsapp

            # Always persist profile changes made above
            user.profile.save()

            # Auto login after registration
            # Pass explicit backend — required when multiple auth backends are configured (allauth + ModelBackend)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Different messages based on role
            if user.profile.is_instructor:
                messages.success(
                    request, 
                    'Cadastro realizado com sucesso! Sua conta foi criada.'
                )
                # Redirect to success page with instructions
                return redirect('accounts:registration_success')
            else:
                messages.success(request, 'Conta criada com sucesso! Bem-vindo ao TREINACNH.')
                return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def registration_success_view(request):
    """
    Success page after registration with next steps information.
    Only accessible to authenticated users.
    """
    return render(request, 'accounts/registration_success.html', {
        'seo_title': 'Cadastro Realizado | TreinaCNH',
        'seo_description': 'Seu cadastro na TreinaCNH foi realizado com sucesso. Confira os próximos passos.',
    })


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    """User login view with rate limiting protection"""
    if request.user.is_authenticated:
        return redirect('marketplace:my_leads')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo de volta, {user.first_name or user.username}!')
                
                # Ignore 'next' parameter - always go to my_leads
                return redirect('marketplace:my_leads')
            else:
                messages.error(request, 'Usuário ou senha incorretos.')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('core:home')


@login_required
def dashboard_view(request):
    """
    User dashboard - different content based on role.
    For students: redirect to cities_list (all instructors)
    For instructors: redirect to my_leads (contacts received)
    """
    profile = request.user.profile
    
    # Instructors go to my_leads
    if profile.is_instructor:
        return redirect('marketplace:my_leads')
    
    # Students go to cities_list using absolute path
    return redirect('/instrutores/cidades/')


@login_required
def complete_profile_view(request):
    """
    Shown after Google login. User must choose: Aluno or Instrutor.
    Marks profile as complete and redirects appropriately.
    Supports ?next= for post-completion redirect to safe internal URLs.
    """
    from django.utils.http import url_has_allowed_host_and_scheme

    profile = request.user.profile

    if profile.is_profile_complete:
        return redirect('accounts:dashboard')

    # Preserve ?next across GET and POST
    next_url = request.POST.get('next') or request.GET.get('next', '')
    next_url_safe = (
        url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
        if next_url
        else False
    )

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            profile.role = role
            profile.is_profile_complete = True
            profile.save()

            if next_url_safe:
                return redirect(next_url)

            if role == RoleChoices.INSTRUCTOR:
                messages.success(
                    request,
                    f'Bem-vindo, {request.user.first_name or request.user.username}! '
                    'Complete seu perfil de instrutor para aparecer no mapa.'
                )
                return redirect('accounts:registration_success')
            else:
                # Students must fill in their personal data before using the platform
                messages.info(
                    request,
                    f'Bem-vindo, {request.user.first_name or request.user.username}! '
                    'Complete seus dados para poder contatar instrutores.'
                )
                complete_url = reverse('accounts:complete_student_data')
                if next_url_safe:
                    complete_url += f'?next={next_url}'
                return redirect(complete_url)
    else:
        form = CompleteProfileForm()

    return render(request, 'accounts/complete_profile.html', {
        'form': form,
        'user': request.user,
        'next': next_url,
        'seo_title': 'Complete seu Cadastro | TreinaCNH',
    })


@login_required
def complete_student_data_view(request):
    """
    Second-step form for students: collects name, email, WhatsApp, CPF,
    CNH categories of interest, and city/state location.
    Students cannot contact instructors until this is done.
    """
    from django.utils.http import url_has_allowed_host_and_scheme
    from django.urls import reverse as _reverse

    profile = request.user.profile

    if not profile.is_student:
        return redirect('accounts:dashboard')

    next_url = request.POST.get('next') or request.GET.get('next', '')
    next_safe = (
        url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},  # must be a set/iterable, not a plain string
            require_https=request.is_secure(),
        )
        if next_url else False
    )

    if request.method == 'POST':
        form = StudentDataForm(request.POST, user=request.user, profile=profile)
        if form.is_valid():
            cd = form.cleaned_data

            # Persist User fields — update_fields avoids touching last_login / password
            user = request.user
            user.first_name = cd['first_name']
            user.last_name = cd['last_name']
            # Only update email when it differs; avoids invalidating provider-verified address
            if cd['email'] and cd['email'] != user.email:
                user.email = cd['email']
            user.save(update_fields=['first_name', 'last_name', 'email'])

            # Persist Profile fields (CPF uniqueness already validated in the form)
            profile.whatsapp_number = cd['whatsapp_number']
            profile.cpf = cd['cpf']
            profile.preferred_city = cd['preferred_city']
            profile.save(update_fields=['whatsapp_number', 'cpf', 'preferred_city'])

            # Save M2M categories; set() handles both add and clear correctly
            from marketplace.models import CategoryCNH
            cats = list(CategoryCNH.objects.filter(code__in=cd['cnh_categories']))
            profile.cnh_categories.set(cats)

            messages.success(
                request,
                '✅ Perfil completo! Agora você pode contatar instrutores na sua cidade.'
            )

            if next_safe:
                return redirect(next_url)
            return redirect('/instrutores/cidades/')
    else:
        form = StudentDataForm(user=request.user, profile=profile)

    return render(request, 'accounts/complete_student_data.html', {
        'form': form,
        'next': next_url,
        'seo_title': 'Complete seu Perfil | TreinaCNH',
    })


@login_required
def profile_edit_view(request):
    """Edit user profile"""
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:profile_edit')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'seo_title': 'Editar Perfil | TreinaCNH',
        'seo_description': 'Atualize suas informações de perfil na TreinaCNH.',
    })
