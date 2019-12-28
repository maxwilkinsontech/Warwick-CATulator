from django.contrib import admin

from .models import User, TabulaDump

admin.site.register(User)
admin.site.register(TabulaDump)