from django import forms

from modules.models import Module


class ModuleForm(forms.ModelForm):
    """
    Form for user to select the Module
    """
    class Meta:
        model = Module
        fields = ['module_code', 'academic_year']
        
    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)
        distinct_module_codes = Module.objects.values_list('module_code', flat=True).order_by('module_code').distinct()

        self.fields['module_code'] = forms.ModelChoiceField(queryset=distinct_module_codes)
        self.fields['module_code'].widget.attrs['class'] = 'mx-2 form-control js-example-responsive'
        self.fields['module_code'].label = 'Module'
        self.fields['academic_year'].widget.attrs['class'] = 'form-control'