from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # Redirect to the login page after successful signup
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})  # Render the signup form template

class MyLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "registration/login.html"

class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = 'wishlist.html'

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = '/password-change-done/'

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'

@login_required
def profile_view(request):
    return render(request, 'profile.html')
