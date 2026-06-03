from django.db import migrations


def _normalize_mobile(raw):
    digits = "".join(c for c in (raw or "") if c.isdigit())
    if len(digits) < 10:
        return ""
    return digits[-10:] if len(digits) > 10 else digits


def migrate_workshop_registrations(apps, schema_editor):
    Workshop = apps.get_model("notes", "WorkshopStudentRegistration")
    Counselling = apps.get_model("notes", "EngineeringCounsellingRegistration")

    existing = {
        _normalize_mobile(m)
        for m in Counselling.objects.values_list("mobile_number", flat=True)
        if _normalize_mobile(m)
    }

    for row in Workshop.objects.all().iterator():
        mobile = _normalize_mobile(row.whatsapp_number)
        if not mobile or mobile in existing:
            continue
        branch_note = (row.standard_year or "").strip()
        if branch_note and len(branch_note) > 200:
            branch_note = branch_note[:200]
        obj = Counselling.objects.create(
            student_name=row.full_name,
            mobile_number=mobile,
            email=row.email or "",
            city=(row.school_college or "—")[:120],
            twelfth_status="passed",
            interested_branch=branch_note,
        )
        Counselling.objects.filter(pk=obj.pk).update(created_at=row.created_at)
        existing.add(mobile)


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0017_engineeringcounsellingregistration"),
    ]

    operations = [
        migrations.RunPython(
            migrate_workshop_registrations,
            migrations.RunPython.noop,
        ),
    ]
