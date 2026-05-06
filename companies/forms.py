from django import forms

from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "source_url",
            "name",
            "applied_on",
            "status",
            "result",
            "has_interview",
            "interview_date",
            "interview_time",
            "interview_format",
            "general_memo",
            "company_memo",
            "interview_memo",
            "reflection_memo",
        ]
        labels = {
            "source_url": "求人・企業URL",
            "name": "会社名",
            "applied_on": "応募日",
            "status": "応募ステータス",
            "result": "結果",
            "has_interview": "面接予定がある",
            "interview_date": "面接日",
            "interview_time": "面接時間",
            "interview_format": "面接形式",
            "general_memo": "通常メモ",
            "company_memo": "企業メモ",
            "interview_memo": "面接メモ",
            "reflection_memo": "反省メモ",
        }
        widgets = {
            "source_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/jobs/...",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "例: 株式会社サンプル",
                }
            ),
            "applied_on": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "result": forms.Select(attrs={"class": "form-select"}),
            "has_interview": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "interview_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                },
                format="%Y-%m-%d",
            ),
            "interview_time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "type": "time",
                },
                format="%H:%M",
            ),
            "interview_format": forms.Select(attrs={"class": "form-select"}),
            "general_memo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "自由メモ、連絡内容、気になったことなど",
                }
            ),
            "company_memo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "事業内容、会社の特徴、求人で気になった点など",
                }
            ),
            "interview_memo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "聞かれたこと、面接官の印象、次回までの準備など",
                }
            ),
            "reflection_memo": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "良かった点、改善点、次に活かすことなど",
                }
            ),
        }
