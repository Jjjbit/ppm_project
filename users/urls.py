from django.urls import path
from .views import SignUpView, MyLoginView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
]