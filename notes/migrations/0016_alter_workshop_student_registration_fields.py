# Manual migration: replace workshop student registration schema (dev-safe; drops old columns).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0015_workshop_student_registration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="student_name",
        ),
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="parent_name",
        ),
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="mobile",
        ),
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="school",
        ),
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="standard",
        ),
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="age",
        ),
        migrations.RemoveField(
            model_name="workshopstudentregistration",
            name="payment_transaction_id",
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="full_name",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="email",
            field=models.EmailField(default="change-me@example.com", max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="school_college",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="standard_year",
            field=models.CharField(default="", help_text="Class / year (e.g. FY, SY, 10th)", max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="whatsapp_number",
            field=models.CharField(db_index=True, default="", max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="payment_transaction_id",
            field=models.CharField(default="", max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workshopstudentregistration",
            name="payment_screenshot",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="workshop_payment_screenshots/",
            ),
        ),
    ]
