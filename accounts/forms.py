from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import phonenumbers
from phonenumbers import geocoder


def country_flag_emoji(country_code: str) -> str:
    return "".join(chr(127397 + ord(char)) for char in country_code.upper())


def get_country_code_choices():
    choices = set()

    for region in phonenumbers.SUPPORTED_REGIONS:
        code = phonenumbers.country_code_for_region(region)
        flag = country_flag_emoji(region)

        try:
            dummy_number = phonenumbers.parse(f"+{code}000000000", region)
            country_name = geocoder.description_for_number(dummy_number, "en")
        except Exception:
            country_name = region

        choices.add((f"+{code}", f"{flag} {country_name} (+{code})"))

    choices = list(choices)
    choices.sort(key=lambda x: int(x[0].replace("+", "")))
    return choices


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Username",
            "class": "form-control"
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "class": "form-control",
        })
    )

    country_code = forms.ChoiceField(
        choices=get_country_code_choices(),
        initial="+91",
        widget=forms.Select(attrs={
            "class": "form-select",
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "8008008001",
            "class": "form-control",
        })
    )

    # ✅ Sirf yahi use karo (default fields)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create Password",
            "class": "form-control",
        })
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm Password",
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


