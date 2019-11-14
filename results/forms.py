from django import forms

from modules.models import Module

class ModuleForm(forms.ModelForm):
    """Form for user to select the Module"""
    module_code = forms.ModelChoiceField(queryset=Module.objects.all())

    class Meta:
        model = Module
        fields = ['module_code', 'academic_year']
        