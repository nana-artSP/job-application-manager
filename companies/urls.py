from django.urls import path

from .views import (
    CompanyCreateView,
    CompanyDeleteView,
    CompanyListView,
    SignupView,
    CompanyUpdateView,
    download_interview_calendar,
    fetch_company_info,
)

app_name = "companies"

urlpatterns = [
    path("", CompanyListView.as_view(), name="list"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("fetch-url/", fetch_company_info, name="fetch_url"),
    path("new/", CompanyCreateView.as_view(), name="create"),
    path("<int:pk>/interview.ics", download_interview_calendar, name="interview_calendar"),
    path("<int:pk>/edit/", CompanyUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", CompanyDeleteView.as_view(), name="delete"),
]
