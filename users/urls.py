from django.urls import path
from .views import SignUpView, MyLoginView, profile_view, CustomPasswordChangeView, CustomPasswordChangeDoneView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("profile/", profile_view, name="profile"),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),

    path('password-change-done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
]