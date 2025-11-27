from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def upgrade(request):
    if request.method == 'POST':
        # Mock payment processing
        user = request.user
        user.is_premium = True
        user.save()
        messages.success(request, "Payment successful! You are now a Premium member.")
        return redirect('home')
    return render(request, 'payments/upgrade.html')
