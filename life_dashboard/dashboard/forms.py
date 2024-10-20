from django import forms
from .models import Stats


class StatsForm(forms.ModelForm):
    class Meta:
        model = Stats
        fields = ['strength', 'agility', 'endurance']
