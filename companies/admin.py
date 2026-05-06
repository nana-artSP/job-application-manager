from django.contrib import admin

from .models import Company


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
