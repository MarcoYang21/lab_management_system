# equipment>forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Reservation

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="用戶名或電子郵件")

    def clean_username(self):
        username = self.cleaned_data['username']
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                raise forms.ValidationError("沒有與此電子郵件關聯的用戶。")
        return username

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['test_name', 'temperature', 'start_time', 'end_time', 'additional_equipment']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }