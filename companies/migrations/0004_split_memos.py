from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0003_company_user"),
    ]

    operations = [
        migrations.RenameField(
            model_name="company",
            old_name="memo",
            new_name="general_memo",
        ),
        migrations.AddField(
            model_name="company",
            name="company_memo",
            field=models.TextField(blank=True, verbose_name="企業メモ"),
        ),
        migrations.AddField(
            model_name="company",
            name="interview_memo",
            field=models.TextField(blank=True, verbose_name="面接メモ"),
        ),
        migrations.AddField(
            model_name="company",
            name="reflection_memo",
            field=models.TextField(blank=True, verbose_name="反省メモ"),
        ),
        migrations.AlterField(
            model_name="company",
            name="general_memo",
            field=models.TextField(blank=True, verbose_name="通常メモ"),
        ),
    ]
