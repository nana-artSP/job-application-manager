from django.urls import path

from .views import (
    CompanyCreateView,
    CompanyDeleteView,
    CompanyListView,
    SignupView,
    CompanyUpdateView,
    TaskCreateView,
    TaskDeleteView,
    TaskListView,
    TaskToggleCompleteView,
    TaskUpdateView,
    download_interview_calendar,
    fetch_company_info,
)

app_name = "companies"

urlpatterns = [
    path("", CompanyListView.as_view(), name="list"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("fetch-url/", fetch_company_info, name="fetch_url"),
    path("new/", CompanyCreateView.as_view(), name="create"),
    path("tasks/", TaskListView.as_view(), name="task_list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task_delete"),
    path("tasks/<int:pk>/toggle/", TaskToggleCompleteView.as_view(), name="task_toggle"),
    path("<int:pk>/interview.ics", download_interview_calendar, name="interview_calendar"),
    path("<int:pk>/edit/", CompanyUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", CompanyDeleteView.as_view(), name="delete"),
]
