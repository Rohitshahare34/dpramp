from django import forms
from .models import ScholarshipRegistration


class ScholarshipRegistrationForm(forms.ModelForm):
    class Meta:
        model = ScholarshipRegistration
        fields = [
            "student_name",
            "parent_guardian_name",
            "age",
            "date_of_birth",
            "gender",
            "school_name",
            "address",
            "email_id",
            "parent_mobile_number",
            "student_class",
            "city",
            "medium",
            "student_photo",
        ]
        labels = {
            "student_name": "Name of student",
            "parent_guardian_name": "Parent/Guardian Name",
            "age": "Age",
            "student_class": "Class (8, 9, 10)",
            "school_name": "School/College Name",
            "address": "Address",
            "email_id": "Email Id",
            "parent_mobile_number": "Parent Contact No. (WhatsApp only)",
        }
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data["mobile_number"].strip()
        if not mobile.isdigit() or len(mobile) != 10:
            raise forms.ValidationError("Enter a valid 10-digit mobile number.")
        return mobile

    def clean_whatsapp_number(self):
        number = self.cleaned_data["whatsapp_number"].strip()
        if not number.isdigit() or len(number) != 10:
            raise forms.ValidationError("Enter a valid 10-digit WhatsApp number.")
        return number

    def clean_parent_mobile_number(self):
        number = self.cleaned_data["parent_mobile_number"].strip()
        if not number.isdigit() or len(number) != 10:
            raise forms.ValidationError("Enter a valid 10-digit parent mobile number.")
        return number

    def clean_age(self):
        age = self.cleaned_data["age"]
        if age < 10 or age > 20:
            raise forms.ValidationError("Enter a valid age between 10 and 20.")
        return age

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Keep model compatibility while collecting only one contact field on form.
        instance.mobile_number = self.cleaned_data["parent_mobile_number"]
        instance.whatsapp_number = self.cleaned_data["parent_mobile_number"]
        if commit:
            instance.save()
        return instance
