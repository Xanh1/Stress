from django.contrib import admin
from .models import CustomUser, Course, Task, StressTest, Question, StudentResponse, ResponseDetail

admin.site.register(CustomUser)
admin.site.register(Task)
admin.site.register(Course)
admin.site.register(StressTest)
admin.site.register(Question)
admin.site.register(StudentResponse)
admin.site.register(ResponseDetail)
