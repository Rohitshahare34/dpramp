from django import forms
from .counselling_constants import COUNSELLING_BRANCH_CHOICES
from .models import (
    ScholarshipRegistration,
    WorkshopStudentRegistration,
    EngineeringCounsellingRegistration,
)


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


class WorkshopStudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = WorkshopStudentRegistration
        fields = [
            "full_name",
            "email",
            "school_college",
            "standard_year",
            "whatsapp_number",
            "payment_transaction_id",
            "payment_screenshot",
        ]
        labels = {
            "full_name": "Full name",
            "email": "Email",
            "school_college": "School / college",
            "standard_year": "Standard / year",
            "whatsapp_number": "WhatsApp number",
            "payment_transaction_id": "Payment transaction ID",
            "payment_screenshot": "Payment screenshot",
        }
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "name", "required": True}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "autocomplete": "email", "required": True}
            ),
            "school_college": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "standard_year": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 10th, FY B.Tech, Second year",
                    "required": True,
                }
            ),
            "whatsapp_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "tel",
                    "inputmode": "numeric",
                    "placeholder": "10-digit WhatsApp number",
                    "required": True,
                }
            ),
            "payment_transaction_id": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "payment_screenshot": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_screenshot"].required = True

    def clean_whatsapp_number(self):
        raw = self.cleaned_data["whatsapp_number"].strip()
        digits = "".join(c for c in raw if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Enter a valid WhatsApp number (at least 10 digits).")
        return digits[-10:] if len(digits) > 10 else digits


class EngineeringCounsellingRegistrationForm(forms.ModelForm):
    class Meta:
        model = EngineeringCounsellingRegistration
        fields = [
            "student_name",
            "mobile_number",
            "email",
            "city",
            "twelfth_status",
            "interested_branch",
        ]
        labels = {
            "student_name": "Student name",
            "mobile_number": "Mobile number",
            "email": "Email ID",
            "city": "City",
            "twelfth_status": "12th appearing / passed",
            "interested_branch": "Interested engineering branch",
        }
        widgets = {
            "student_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Student name", "required": True}
            ),
            "mobile_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mobile number",
                    "inputmode": "numeric",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email (optional)"}
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "City", "required": True}
            ),
            "twelfth_status": forms.Select(attrs={"class": "form-select", "required": True}),
            "interested_branch": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["interested_branch"] = forms.ChoiceField(
            choices=COUNSELLING_BRANCH_CHOICES,
            required=False,
            label="Interested engineering branch",
            widget=forms.Select(attrs={"class": "form-select"}),
        )

    def clean_interested_branch(self):
        return self.cleaned_data.get("interested_branch") or ""

    def clean_mobile_number(self):
        raw = self.cleaned_data["mobile_number"].strip()
        digits = "".join(c for c in raw if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Enter a valid mobile number (at least 10 digits).")
        return digits[-10:] if len(digits) > 10 else digits
