from datetime import datetime, time, timedelta
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect

from .forms import CompanyForm, TaskForm
from .models import Company, Task


def escape_ics_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def format_ics_datetime(value):
    return timezone.localtime(value).strftime("%Y%m%dT%H%M%S")


def order_tasks_by_priority(queryset):
    # ダッシュボードの優先順位:
    # 1. 未完了、2. 高優先度、3. 期限が近い順、4. 新しい順
    return queryset.annotate(
        completion_order=Case(
            When(is_completed=False, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        priority_order=Case(
            When(priority=Task.Priority.HIGH, then=Value(0)),
            When(priority=Task.Priority.MEDIUM, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        ),
        due_order=Case(
            When(due_date__isnull=False, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
    ).order_by("completion_order", "priority_order", "due_order", "due_date", "-created_at")


class CompanyPageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.h1 = ""
        self._current_tag = None
        self._title_parts = []
        self._h1_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._current_tag = tag
        if tag == "meta":
            name = attrs.get("name", "").lower()
            prop = attrs.get("property", "").lower()
            if name == "description" or prop == "og:description":
                self.description = attrs.get("content", "").strip()
        if tag == "title":
            self._title_parts = []
        if tag == "h1" and not self.h1:
            self._h1_parts = []

    def handle_data(self, data):
        if self._current_tag == "title":
            self._title_parts.append(data)
        if self._current_tag == "h1" and not self.h1:
            self._h1_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self.title = " ".join(self._title_parts).strip()
        if tag == "h1" and not self.h1:
            self.h1 = " ".join(self._h1_parts).strip()
        self._current_tag = None


def guess_company_name(title, h1):
    source = h1 or title
    for separator in ["｜", "|", " - ", "【", "「"]:
        if separator in source:
            source = source.split(separator)[0]
    return source.strip()[:100]


@login_required
@require_GET
def fetch_company_info(request):
    target_url = request.GET.get("url", "").strip()
    parsed = urlparse(target_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return JsonResponse({"error": "有効なURLを入力してください。"}, status=400)

    try:
        req = Request(
            target_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; JobApplicationManager/1.0)"},
        )
        with urlopen(req, timeout=8) as response:
            content_type = response.headers.get("Content-Type", "")
            charset = response.headers.get_content_charset() or "utf-8"
            if "html" not in content_type:
                return JsonResponse({"error": "HTMLページではないため取得できませんでした。"}, status=400)
            html = response.read(500000).decode(charset, errors="replace")
    except (HTTPError, URLError, TimeoutError, ValueError):
        return JsonResponse({"error": "URLから情報を取得できませんでした。"}, status=400)

    parser = CompanyPageParser()
    parser.feed(html)
    name = guess_company_name(parser.title, parser.h1)
    memo_parts = [
        part
        for part in [
            f"ページタイトル: {parser.title}" if parser.title else "",
            f"概要: {parser.description}" if parser.description else "",
            f"URL: {target_url}",
        ]
        if part
    ]

    return JsonResponse(
        {
            "name": name,
            "memo": "\n".join(memo_parts),
        }
    )


@login_required
@require_GET
def download_interview_calendar(request, pk):
    company = Company.objects.filter(user=request.user, pk=pk, has_interview=True).first()
    if not company or not company.interview_date:
        return HttpResponse("面接日が登録されていません。", status=400, content_type="text/plain; charset=utf-8")

    start_time = company.interview_time or time(9, 0)
    starts_at = timezone.make_aware(datetime.combine(company.interview_date, start_time))
    ends_at = starts_at + timedelta(hours=1)
    now = timezone.now()
    title = f"{company.name} 面接"
    description_parts = [
        company.interview_schedule_display,
        company.interview_memo,
        company.source_url,
    ]
    description = "\n".join(part for part in description_parts if part)

    ics = "\r\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Job Application Manager//Interview Calendar//JA",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:company-{company.pk}-interview@job-application-manager.local",
            f"DTSTAMP:{format_ics_datetime(now)}",
            f"DTSTART:{format_ics_datetime(starts_at)}",
            f"DTEND:{format_ics_datetime(ends_at)}",
            f"SUMMARY:{escape_ics_text(title)}",
            f"DESCRIPTION:{escape_ics_text(description)}",
            "END:VEVENT",
            "END:VCALENDAR",
            "",
        ]
    )
    response = HttpResponse(ics, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="interview-{company.pk}.ics"'
    return response


class SignupView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        should_claim_legacy_companies = not get_user_model().objects.exists()
        user = form.save()
        if should_claim_legacy_companies:
            Company.objects.filter(user__isnull=True).update(user=user)
        login(self.request, user)
        return super().form_valid(form)


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = "companies"
    template_name = "companies/company_list.html"

    tab_filters = {
        "active": [Company.Result.IN_PROGRESS],
        "rejected": [
            Company.Result.DOCUMENT_REJECTED,
            Company.Result.FIRST_INTERVIEW_REJECTED,
            Company.Result.SECOND_INTERVIEW_REJECTED,
            Company.Result.DECLINED,
        ],
        "passed": [Company.Result.PASSED],
    }

    def base_queryset(self):
        return Company.objects.filter(user=self.request.user)

    def get_queryset(self):
        current_tab = self.request.GET.get("tab", "all")
        queryset = self.base_queryset()
        if current_tab == "interview":
            queryset = queryset.filter(has_interview=True)
        elif current_tab in self.tab_filters:
            queryset = queryset.filter(result__in=self.tab_filters[current_tab])

        return queryset.annotate(
            result_priority=Case(
                When(result=Company.Result.IN_PROGRESS, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by("result_priority", "-applied_on", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = self.base_queryset()
        total_count = base_queryset.count()
        active_count = base_queryset.filter(result=Company.Result.IN_PROGRESS).count()
        interview_count = base_queryset.filter(has_interview=True).count()
        upcoming_interviews = base_queryset.filter(
            has_interview=True,
            interview_date__gte=timezone.localdate(),
        ).order_by("interview_date", "interview_time", "created_at")[:3]
        priority_tasks = order_tasks_by_priority(
            Task.objects.filter(user=self.request.user, is_completed=False).select_related("company")
        )[:5]
        unresolved_companies = base_queryset.filter(
            status=Company.Status.APPLIED,
            result=Company.Result.IN_PROGRESS,
        )[:5]
        interview_without_schedule = base_queryset.filter(
            status=Company.Status.INTERVIEW,
            has_interview=False,
        )[:5]
        rejected_count = base_queryset.filter(result__in=self.tab_filters["rejected"]).count()
        passed_count = base_queryset.filter(result=Company.Result.PASSED).count()
        context.update(
            {
                "current_tab": self.request.GET.get("tab", "all"),
                "total_count": total_count,
                "active_count": active_count,
                "interview_count": interview_count,
                "upcoming_interviews": upcoming_interviews,
                "priority_tasks": priority_tasks,
                "unresolved_companies": unresolved_companies,
                "interview_without_schedule": interview_without_schedule,
                "rejected_count": rejected_count,
                "passed_count": passed_count,
                "tabs": [
                    {"key": "all", "label": "すべて", "count": total_count},
                    {"key": "active", "label": "選考中", "count": active_count},
                    {"key": "interview", "label": "面接予定", "count": interview_count},
                    {"key": "rejected", "label": "落ちた・辞退", "count": rejected_count},
                    {"key": "passed", "label": "合格", "count": passed_count},
                ],
            }
        )
        return context


class TaskQuerysetMixin(LoginRequiredMixin):
    model = Task

    def get_queryset(self):
        # 他ユーザーのタスクを閲覧・編集・削除できないように、常にログインユーザーで絞ります。
        return Task.objects.filter(user=self.request.user).select_related("company")


class TaskListView(TaskQuerysetMixin, ListView):
    context_object_name = "tasks"
    template_name = "tasks/task_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return order_tasks_by_priority(queryset)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("companies:task_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        # ここでログインユーザーとタスクを紐付けます。
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(TaskQuerysetMixin, UpdateView):
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("companies:task_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TaskDeleteView(TaskQuerysetMixin, DeleteView):
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("companies:task_list")


class TaskToggleCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # 完了切り替えも他ユーザーのタスクを対象にできないようにします。
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.is_completed = not task.is_completed
        task.save(update_fields=["is_completed"])
        return redirect(request.POST.get("next") or reverse_lazy("companies:task_list"))


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:list")

    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = "companies/company_confirm_delete.html"
    success_url = reverse_lazy("companies:list")

    def get_queryset(self):
        return Company.objects.filter(user=self.request.user)
