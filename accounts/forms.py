# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# All country codes
COUNTRY_CODE_CHOICES = [
    ('+91', '🇮🇳 +91 India'),
    ('+1', '🇺🇸 +1 USA'),
    ('+44', '🇬🇧 +44 UK'),
    ('+61', '🇦🇺 +61 Australia'),
    ('+81', '🇯🇵 +81 Japan'),
    ('+971', '🇦🇪 +971 UAE'),
    ('+92', '🇵🇰 +92 Pakistan'),
    ('+880', '🇧🇩 +880 Bangladesh'),
    ('+94', '🇱🇰 +94 Sri Lanka'),
    ('+977', '🇳🇵 +977 Nepal'),
    ('+86', '🇨🇳 +86 China'),
    ('+49', '🇩🇪 +49 Germany'),
    ('+33', '🇫🇷 +33 France'),
    ('+39', '🇮🇹 +39 Italy'),
    ('+7', '🇷🇺 +7 Russia'),
]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "class": "form-control",
        })
    )

    country_code = forms.ChoiceField(
        choices=COUNTRY_CODE_CHOICES,
        initial="+91",
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "9876543210",
            "class": "form-control",
        })
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "country_code",
            "phone",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
