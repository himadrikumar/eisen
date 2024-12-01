from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['text', 'category']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Enter task here...'}),
            'category': forms.Select()
        }