from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


@login_required
def index(request):
    token = Token.objects.get_or_create(user=request.user)[0]
    context = {'user': token.user, 'token': token.key}
    return render(request, 'index.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            return redirect('login')
        context = {'form': form}
    else:
        context = {}

    return render(request, 'registration/register.html', context)
