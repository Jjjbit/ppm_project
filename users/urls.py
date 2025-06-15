from django.urls import path
from .views import SignUpView, MyLoginView, ProfileView, CustomPasswordChangeView, CustomPasswordChangeDoneView, \
    edit_profile_view, ProfileView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('profile/edit-profile/', edit_profile_view, profile_view, name='edit_profile'),  # Assuming edit_profile_view is the same as profile_view for simplicity
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),

    path('password-change-done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
]