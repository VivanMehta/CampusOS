from django.contrib import admin

from .models import (
    Semester,
    Course,
    GradeCategory,
    GradeItem,
    Assignment,
    CalendarEvent,
)

admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(GradeCategory)
admin.site.register(GradeItem)
admin.site.register(Assignment)
admin.site.register(CalendarEvent)