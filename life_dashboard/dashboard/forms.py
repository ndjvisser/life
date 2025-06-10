from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        print("[DEBUG] Saving user registration form")
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            print("[DEBUG] Committing user to database")
            user.save()
            print(f"[DEBUG] User saved with ID: {user.id}")
        return user

    def clean(self):
        print("[DEBUG] Cleaning registration form data")
        cleaned_data = super().clean()
        print(f"[DEBUG] Cleaned data: {cleaned_data}")
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "email")
