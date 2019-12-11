from django.contrib import admin

from .models import Module, AssessmentGroup, Assessment, Course, UndefinedModule

class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 0

class AssessmentGroupInline(admin.TabularInline):
    model = AssessmentGroup
    extra = 0
    show_change_link = True

class AssessmentGroupAdmin(admin.ModelAdmin):
    model = AssessmentGroup
    inlines = [AssessmentInline]

class ModuleAdmin(admin.ModelAdmin):
    model = Module
    inlines = [AssessmentGroupInline]
    list_filter = ('academic_year',)

admin.site.register(Module, ModuleAdmin)
admin.site.register(AssessmentGroup, AssessmentGroupAdmin)
admin.site.register(Assessment)
admin.site.register(Course)
admin.site.register(UndefinedModule)
