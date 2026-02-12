"""
Views for authentication and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django_ratelimit.decorators import ratelimit
from .forms import UserRegistrationForm, CustomLoginForm, ProfileEditForm
from .models import Profile


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
            
            # Process instructor extra fields if provided
            if user.profile.is_instructor:
                whatsapp = request.POST.get('whatsapp', '').strip()
                if whatsapp:
                    user.profile.whatsapp_number = whatsapp
                    user.profile.save()
            
            # Auto login after registration
            login(request, user)
            
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
    return render(request, 'accounts/registration_success.html')


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
def profile_edit_view(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ProfileEditForm(instance=profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})
