from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.utils import timezone
from dateutil.relativedelta import relativedelta

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(min_length=5, max_length=20)

    class Meta:
        model = User
        fields = ('username', 'email')

class AdminUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, label="Senha Provisória")
    VALIDITY_CHOICES = [
        ('1_day', 'Teste (1 Dia)'),
        ('1_month', '1 Mês'),
        ('3_months', '3 Meses'),
        ('6_months', '6 Meses'),
        ('12_months', '1 Ano'),
    ]
    validity_period = forms.ChoiceField(choices=VALIDITY_CHOICES, label="Período de Validade")

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        period = self.cleaned_data['validity_period']
        if period == '1_day':
            user.valid_until = timezone.now().date() + relativedelta(days=1)
        elif period == '1_month':
            user.valid_until = timezone.now().date() + relativedelta(months=1)
        elif period == '3_months':
            user.valid_until = timezone.now().date() + relativedelta(months=3)
        elif period == '6_months':
            user.valid_until = timezone.now().date() + relativedelta(months=6)
        elif period == '12_months':
            user.valid_until = timezone.now().date() + relativedelta(years=1)
        
        if commit:
            user.save()
        return user

class AdminUserEditForm(forms.ModelForm):
    valid_until = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Válido até")
    
    class Meta:
        model = User
        fields = ('valid_until',)

class AdminUserUpdateForm(forms.ModelForm):
    phone = forms.CharField(required=False, label="Celular")
    valid_until = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Válido até", required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'valid_until')
