from django.urls import path
from .views import SignUpView, MyLoginView, edit_profile_view, ProfileView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('edit-profile/', edit_profile_view, name='edit_profile'),
    path('password-change/', auth_views.PasswordChangeView.as_view( template_name='registration/password_change_form.html'), name='password_change'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view( template_name='registration/password_change_done.html'), name='password_change_done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]