from django import forms

from modules.models import Module


class ModuleForm(forms.ModelForm):
    """Form for user to select the Module"""
    module_code = forms.ModelChoiceField(queryset=Module.objects.all())

    class Meta:
        model = Module
        fields = ['module_code', 'academic_year']
        
    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        self.fields['module_code'].widget.attrs['class'] = 'form-control mb-2'
        self.fields['module_code'].label = 'Module'
        self.fields['academic_year'].widget.attrs['class'] = 'form-control'