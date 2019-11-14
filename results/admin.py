from django.contrib import admin

from .models import YearGrade, ModuleResult, AssessmentResult

class ModuleResultInline(admin.TabularInline):
    model = ModuleResult
    extra = 0
    show_change_link = True

class AssessmentResultInline(admin.TabularInline):
    model = AssessmentResult
    extra = 0
    show_change_link = True

class ModuleResultAdmin(admin.ModelAdmin):
    model = ModuleResult
    inlines = [AssessmentResultInline]
    

class YearGradeAdmin(admin.ModelAdmin):
    model = YearGrade
    inlines = [ModuleResultInline]

admin.site.register(YearGrade, YearGradeAdmin)
admin.site.register(ModuleResult, ModuleResultAdmin)
admin.site.register(AssessmentResult)
