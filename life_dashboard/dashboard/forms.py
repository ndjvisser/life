from django import forms
from .models import Stats
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class StatsForm(forms.ModelForm):
    class Meta:
        model = Stats
        fields = [
            'strength',
            'agility',
            'endurance',
            'intelligence',
            'charisma',
            'wisdom'
            ]

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
