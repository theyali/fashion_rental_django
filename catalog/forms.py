from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import ContactMessage, Reservation


User = get_user_model()


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["customer_name", "email", "phone", "start_date", "end_date", "color", "size", "notes"]


class EmailLoginForm(forms.Form):
    email = forms.EmailField(max_length=150)
    password = forms.CharField(strip=False, widget=forms.PasswordInput)
    user_cache = None

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").strip().lower()
        password = cleaned.get("password")
        if not email or not password:
            return cleaned
        user = User.objects.filter(email__iexact=email).first()
        if user:
            self.user_cache = authenticate(self.request, username=user.get_username(), password=password)
        if self.user_cache is None:
            raise forms.ValidationError("Email və ya şifrə yanlışdır.")
        if not self.user_cache.is_active:
            raise forms.ValidationError("Bu hesab deaktiv edilib.")
        return cleaned

    def get_user(self):
        return self.user_cache


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Bu email ilə hesab artıq mövcuddur.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        if commit:
            user.save()
        return user
