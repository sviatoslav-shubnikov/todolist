from django.contrib import admin
from .models import User, Category, Task
from django.contrib import admin
from django_celery_beat.models import (  
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)
from django.contrib.auth.models import User as AuthUser, Group


admin.site.unregister(Group)
admin.site.unregister(AuthUser)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(SolarSchedule)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('TelegramId', 'id', 'CreatedAt', 'UpdatedAt')
    search_fields = ('TelegramId',)
    readonly_fields = ('id', 'CreatedAt', 'UpdatedAt')
    


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('Name', 'User', 'id', 'CreatedAt', 'UpdatedAt')
    search_fields = ('Name', 'User__TelegramId')
    list_filter = ('User',)
    readonly_fields = ('id', 'CreatedAt', 'UpdatedAt')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('Title', 'User', 'Status', 'DueDate', 'IsNotified', 'id', 'CreatedAt', 'UpdatedAt')
    search_fields = ('Title', 'Description', 'User__TelegramId')
    list_filter = ('Status', 'IsNotified', 'User')
    filter_horizontal = ('Categories',)
    readonly_fields = ('id', 'CreatedAt', 'UpdatedAt')
