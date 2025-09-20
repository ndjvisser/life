import logging

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        logger.debug("Saving user registration form")
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            logger.debug("Committing user to database")
            user.save()
            logger.debug("User saved with ID: %s", user.id)
        return user

    def clean(self):
        logger.debug("Cleaning registration form data")
        cleaned_data = super().clean()
        logger.debug("Cleaned data: %s", cleaned_data)
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ["bio", "location", "birth_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update User model fields
            user = profile.user
            if self.cleaned_data.get("first_name"):
                user.first_name = self.cleaned_data["first_name"]
            if self.cleaned_data.get("last_name"):
                user.last_name = self.cleaned_data["last_name"]
            if self.cleaned_data.get("email"):
                user.email = self.cleaned_data["email"]
            user.save()
            profile.save()
        return profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = []  # Remove fields that do not belong to UserProfile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            user = profile.user
            if self.cleaned_data.get("first_name"):
                user.first_name = self.cleaned_data["first_name"]
            if self.cleaned_data.get("last_name"):
                user.last_name = self.cleaned_data["last_name"]
            if self.cleaned_data.get("email"):
                user.email = self.cleaned_data["email"]
            user.save()
            profile.save()
        return profile
