from datetime import datetime, time, timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time


class Company(models.Model):
    class Status(models.TextChoices):
        CONSIDERING = "considering", "検討中"
        APPLIED = "applied", "応募済み"
        DOCUMENT_SCREENING = "document_screening", "書類選考"
        INTERVIEW = "interview", "面接"
        OFFER = "offer", "内定"
        REJECTED = "rejected", "不採用"
        DECLINED = "declined", "辞退"

    class Result(models.TextChoices):
        IN_PROGRESS = "in_progress", "選考中"
        DOCUMENT_REJECTED = "document_rejected", "書類落ち"
        FIRST_INTERVIEW_REJECTED = "first_interview_rejected", "1次面接落ち"
        SECOND_INTERVIEW_REJECTED = "second_interview_rejected", "2次面接落ち"
        PASSED = "passed", "合格"
        DECLINED = "declined", "辞退"

    class InterviewFormat(models.TextChoices):
        ONLINE = "online", "オンライン"
        IN_PERSON = "in_person", "対面"
        PHONE = "phone", "電話"
        OTHER = "other", "その他"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
        verbose_name="ユーザー",
        null=True,
        blank=True,
    )
    name = models.CharField("会社名", max_length=100)
    source_url = models.URLField("求人・企業URL", blank=True)
    applied_on = models.DateField("応募日", null=True, blank=True)
    status = models.CharField(
        "応募ステータス",
        max_length=30,
        choices=Status.choices,
        default=Status.CONSIDERING,
    )
    result = models.CharField(
        "結果",
        max_length=30,
        choices=Result.choices,
        default=Result.IN_PROGRESS,
    )
    has_interview = models.BooleanField("面接予定がある", default=False)
    interview_date = models.DateField("面接日", null=True, blank=True)
    interview_time = models.TimeField("面接時間", null=True, blank=True)
    interview_format = models.CharField(
        "面接形式",
        max_length=20,
        choices=InterviewFormat.choices,
        blank=True,
    )
    general_memo = models.TextField("通常メモ", blank=True)
    company_memo = models.TextField("企業メモ", blank=True)
    interview_memo = models.TextField("面接メモ", blank=True)
    reflection_memo = models.TextField("反省メモ", blank=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "会社"
        verbose_name_plural = "会社"

    @property
    def result_badge_class(self):
        if self.result == self.Result.IN_PROGRESS:
            return "text-bg-primary"
        if self.result == self.Result.PASSED:
            return "text-bg-success"
        if self.result == self.Result.DECLINED:
            return "text-bg-dark"
        return "text-bg-danger"

    @property
    def memo_preview(self):
        for memo in [
            self.general_memo,
            self.company_memo,
            self.interview_memo,
            self.reflection_memo,
        ]:
            if memo:
                return memo
        return ""

    @property
    def interview_schedule_display(self):
        if not self.has_interview:
            return ""
        interview_date = self.interview_date
        interview_time = self.interview_time
        if isinstance(interview_date, str):
            interview_date = parse_date(interview_date)
        if isinstance(interview_time, str):
            interview_time = parse_time(interview_time)

        parts = []
        if interview_date:
            parts.append(interview_date.strftime("%Y/%m/%d"))
        if interview_time:
            parts.append(interview_time.strftime("%H:%M"))
        if self.interview_format:
            parts.append(self.get_interview_format_display())
        return " ".join(parts) or "予定あり"

    @property
    def google_calendar_url(self):
        if not self.has_interview or not self.interview_date:
            return ""

        interview_date = self.interview_date
        interview_time = self.interview_time
        if isinstance(interview_date, str):
            interview_date = parse_date(interview_date)
        if isinstance(interview_time, str):
            interview_time = parse_time(interview_time)
        if not interview_date:
            return ""

        start_time = interview_time or time(9, 0)
        starts_at = timezone.make_aware(datetime.combine(interview_date, start_time))
        ends_at = starts_at + timedelta(hours=1)
        details = "\n".join(
            part
            for part in [
                self.interview_schedule_display,
                self.interview_memo,
                self.source_url,
            ]
            if part
        )
        params = urlencode(
            {
                "action": "TEMPLATE",
                "text": f"{self.name} 面接",
                "dates": (
                    f"{timezone.localtime(starts_at).strftime('%Y%m%dT%H%M%S')}/"
                    f"{timezone.localtime(ends_at).strftime('%Y%m%dT%H%M%S')}"
                ),
                "details": details,
            }
        )
        return f"https://calendar.google.com/calendar/render?{params}"

    def __str__(self):
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        HIGH = "high", "高"
        MEDIUM = "medium", "中"
        LOW = "low", "低"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="ユーザー",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="企業",
        null=True,
        blank=True,
    )
    title = models.CharField("タスク名", max_length=120)
    description = models.TextField("詳細", blank=True)
    priority = models.CharField(
        "優先度",
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    due_date = models.DateField("期限", null=True, blank=True)
    is_completed = models.BooleanField("完了", default=False)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        ordering = ["is_completed", "due_date", "-created_at"]
        verbose_name = "タスク"
        verbose_name_plural = "タスク"

    @property
    def priority_badge_class(self):
        if self.priority == self.Priority.HIGH:
            return "text-bg-danger"
        if self.priority == self.Priority.LOW:
            return "text-bg-secondary"
        return "text-bg-primary"

    @property
    def is_overdue(self):
        return bool(
            self.due_date
            and not self.is_completed
            and self.due_date < timezone.localdate()
        )

    def __str__(self):
        return self.title
