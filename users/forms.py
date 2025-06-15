from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    is_store_manager = forms.BooleanField(label="Register as seller?", required=False)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            'address',
            'is_store_manager',
            'password1',
            'password2'
        )  # new

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            'address',
        ) # new

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "password",
        )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive.",
                code="inactive",
            )



