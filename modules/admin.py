from django.contrib import admin

from .models import Module, AssessmentGroup, Assessment, Course, UndefinedModule

class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 0

class AssessmentGroupInline(admin.TabularInline):
    model = AssessmentGroup
    extra = 0
    show_change_link = True

class AssessmentAdmin(admin.ModelAdmin):
    model = Assessment
    search_fields = ('assessment_name', 'assessment_group__assessment_group_name',)
    ordering = ('assessment_name',)

class AssessmentGroupAdmin(admin.ModelAdmin):
    model = AssessmentGroup
    inlines = [AssessmentInline]
    search_fields = ('module__module_code', 'module__module_name',)

class ModuleAdmin(admin.ModelAdmin):
    model = Module
    inlines = [AssessmentGroupInline]
    list_filter = ('academic_year',)
    search_fields = ('module_code', 'module_name',)

admin.site.register(Module, ModuleAdmin)
admin.site.register(AssessmentGroup, AssessmentGroupAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Course)
admin.site.register(UndefinedModule)
