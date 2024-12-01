from django.contrib import admin
from .models import CustomUser, Course, Task

admin.site.register(CustomUser)
admin.site.register(Task)
admin.site.register(Course)
