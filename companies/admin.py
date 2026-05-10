from django.contrib import admin

from .models import Company, Task


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "status",
        "result",
        "applied_on",
        "has_interview",
        "interview_date",
        "interview_time",
        "created_at",
    )
    list_filter = ("status", "result", "has_interview", "interview_format")
    search_fields = (
        "name",
        "general_memo",
        "company_memo",
        "interview_memo",
        "reflection_memo",
        "user__username",
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "company", "priority", "due_date", "is_completed", "created_at")
    list_filter = ("priority", "is_completed", "due_date")
    search_fields = ("title", "description", "company__name", "user__username")
