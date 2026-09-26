from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Category, Color, ContactMessage, Product, ProductImage, ProductVideo, Reservation


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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput)
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data and self.required:
            raise forms.ValidationError(self.error_messages["required"], code="required")
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleFileField, self).clean(file_item, initial) for file_item in files]


class ProductSubmissionForm(forms.Form):
    LISTING_RENTAL = "rental"
    LISTING_SALE = "sale"
    LISTING_BOTH = "both"
    LISTING_CHOICES = [(LISTING_RENTAL, "Kirayə"), (LISTING_SALE, "Satış"), (LISTING_BOTH, "Satış və kirayə")]

    listing_type = forms.ChoiceField(choices=LISTING_CHOICES)
    category = forms.ModelChoiceField(queryset=Category.objects.none())
    name = forms.CharField(max_length=180)
    brand = forms.CharField(max_length=160, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))
    material = forms.CharField(max_length=180, required=False)
    length = forms.CharField(max_length=180, required=False)
    care = forms.CharField(max_length=220, required=False)
    extra_details = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    additional_note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    sizes = forms.CharField(max_length=120, help_text="Məsələn: XS, S, M, L")
    colors = forms.ModelMultipleChoiceField(queryset=Color.objects.none(), required=False)
    rental_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
    min_rental_days = forms.IntegerField(min_value=3, max_value=60, initial=3, required=False)
    images = MultipleFileField(required=True)
    videos = MultipleFileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self.fields["colors"].queryset = Color.objects.all()

    def clean(self):
        cleaned = super().clean()
        listing_type = cleaned.get("listing_type")
        rental_price = cleaned.get("rental_price")
        sale_price = cleaned.get("sale_price")
        if listing_type in {self.LISTING_RENTAL, self.LISTING_BOTH} and rental_price is None:
            self.add_error("rental_price", "Kirayə qiymətini qeyd edin.")
        if listing_type in {self.LISTING_SALE, self.LISTING_BOTH} and sale_price is None:
            self.add_error("sale_price", "Satış qiymətini qeyd edin.")
        return cleaned


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
