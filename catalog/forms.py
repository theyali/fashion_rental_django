from django import forms
from .models import ContactMessage, Reservation


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["customer_name", "email", "phone", "start_date", "end_date", "color", "notes"]
