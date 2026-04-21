from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
# Create your views here.

# Registro
# ==============================



def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada correctamente")
            return redirect('boards:list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})





# ==============================
# Login
# ==============================
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('boards:list')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})




# ==============================
# Logout
# ==============================
def logout_view(request):
    logout(request)
    return redirect('/')





# ==============================
# Perfil
# ==============================
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

