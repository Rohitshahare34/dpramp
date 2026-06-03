# Generated manually for engineering counselling registrations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0016_alter_workshop_student_registration_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="EngineeringCounsellingRegistration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("student_name", models.CharField(max_length=200)),
                ("mobile_number", models.CharField(db_index=True, max_length=15)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("city", models.CharField(max_length=120)),
                (
                    "twelfth_status",
                    models.CharField(
                        choices=[
                            ("appearing", "12th Appearing"),
                            ("passed", "12th Passed"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "interested_branch",
                    models.CharField(blank=True, default="", max_length=200),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Engineering Counselling Registration",
                "verbose_name_plural": "Engineering Counselling Registrations",
                "ordering": ["-created_at"],
            },
        ),
    ]
