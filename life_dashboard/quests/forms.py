from django import forms
from .models import Quest, Habit, HabitCompletion

class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['title', 'description', 'quest_type', 'status', 'experience_reward', 'start_date', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'validate'}),
            'description': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            'quest_type': forms.Select(attrs={'class': 'browser-default'}),
            'status': forms.Select(attrs={'class': 'browser-default'}),
            'experience_reward': forms.NumberInput(attrs={'class': 'validate'}),
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'due_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'description', 'frequency', 'target_count']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'validate'}),
            'description': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            'frequency': forms.Select(attrs={'class': 'browser-default'}),
            'target_count': forms.NumberInput(attrs={'class': 'validate'}),
        }

class HabitCompletionForm(forms.ModelForm):
    class Meta:
        model = HabitCompletion
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        } 