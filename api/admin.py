from django.contrib import admin
from django.contrib.auth import get_user_model
# from .models import *
# Register your models here.
User = get_user_model()

# admin.site.register(List)
# admin.site.register(Task)
admin.site.register(User)