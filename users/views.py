from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from .forms import CustomUserCreationForm, CustomAuthenticationForm

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
