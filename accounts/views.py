from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('home')
        else:
            messages.error(request, 'Erro ao criar conta. Verifique os dados abaixo.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_confirm(request):
    return render(request, 'accounts/logout.html')

from django.contrib.auth.decorators import user_passes_test
from .forms import AdminUserCreationForm, AdminUserEditForm, AdminUserUpdateForm
from .models import User
from django.shortcuts import get_object_or_404

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
def user_create(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('user_create')
        else:
            messages.error(request, 'Erro ao criar usuário.')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'accounts/user_create.html', {'form': form, 'users': users})

@user_passes_test(lambda u: u.is_superuser)
def edit_user_validity(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Validade do usuário atualizada!')
        else:
            messages.error(request, 'Erro ao atualizar validade.')
    return redirect('user_list')

@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('user_list')
    else:
        form = AdminUserUpdateForm(instance=user)
    
    return render(request, 'accounts/edit_user.html', {'form': form, 'target_user': user})

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('user_list')
