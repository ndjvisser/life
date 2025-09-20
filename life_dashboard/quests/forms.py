from django import forms

from .models import Habit, HabitCompletion, Quest


class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = [
            "title",
            "description",
            "difficulty",
            "quest_type",
            "experience_reward",
            "start_date",
            "due_date",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "validate"}),
            "description": forms.Textarea(
                attrs={"rows": 3, "class": "materialize-textarea"}
            ),
            "difficulty": forms.Select(attrs={"class": "browser-default"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class HabitForm(forms.ModelForm):
    experience_reward = forms.IntegerField(
        min_value=0, widget=forms.NumberInput(attrs={"class": "validate"})
    )
    target_count = forms.IntegerField(
        min_value=1, widget=forms.NumberInput(attrs={"class": "validate"})
    )

    class Meta:
        model = Habit
        fields = [
            "name",
            "description",
            "frequency",
            "target_count",
            "experience_reward",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "validate"}),
            "description": forms.Textarea(attrs={"class": "materialize-textarea"}),
            "frequency": forms.Select(attrs={"class": "browser-default"}),
        }


class HabitCompletionForm(forms.ModelForm):
    class Meta:
        model = HabitCompletion
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"class": "materialize-textarea"}),
        }
