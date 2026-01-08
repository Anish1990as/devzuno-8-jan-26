from django import forms
from .models import ContactMessage
import re

# -------------------------------
# Helpers: language choices (pycountry) with safe fallback
# -------------------------------
def build_language_choices():
    try:
        import pycountry
        seen = set()
        out = []
        for lang in pycountry.languages:
            code = getattr(lang, "alpha_2", None) or getattr(lang, "bibliographic", None) or getattr(lang, "terminology", None)
            name = getattr(lang, "name", None)
            if not code or not name:
                continue
            key = (code.lower(), name)
            if key in seen:
                continue
            seen.add(key)
            out.append((code.lower(), name))
        return sorted(out, key=lambda x: x[1].lower())
    except Exception:
        # Minimal fallback
        return [("en", "English"), ("hi", "Hindi"), ("es", "Spanish"), ("ar", "Arabic")]

LANGUAGE_CHOICES = build_language_choices()

# Local (visible) phone validation
PHONE_LOCAL_RE = re.compile(r"^[0-9][0-9\s\-()]{6,}$")

class ContactForm(forms.ModelForm):
    # Country code is captured by intl-tel-input; we keep it hidden and fill via JS (+91, +1, ...)
    country_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Preferred languages (multi + allow custom via Select2 tags)
    languages = forms.MultipleChoiceField(
        required=False,
        choices=LANGUAGE_CHOICES,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "id": "id_languages"})
    )

    class Meta:
        model = ContactMessage
        fields = [
            "name", "phone", "email",
            "location", "pincode",
            "website_type", "support_language",
            "languages", "message", "country_code",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            # NOTE: id set below in __init__ so JS can find it
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "City, Country"}),
            "pincode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Postal/ZIP code"}),
            "website_type": forms.Select(attrs={"class": "form-select"}),
            "support_language": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Tell us about your project…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # mark required like Zauca
        self.fields["name"].required = True
        self.fields["phone"].required = True
        self.fields["email"].required = True
        self.fields["website_type"].required = True
        self.fields["support_language"].required = True

        # ids used by template JS
        self.fields["phone"].widget.attrs.update({"id": "id_phone_visible", "inputmode": "tel", "autocomplete": "tel"})
        self.fields["country_code"].widget.attrs.update({"id": "id_country_code_hidden"})

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not PHONE_LOCAL_RE.match(phone):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    # Accept user-added tags from Select2 (not limited to fixed choices)
    def clean_languages(self):
        raw = self.data.getlist("languages")
        cleaned = [v.strip() for v in raw if v.strip()]
        return cleaned
