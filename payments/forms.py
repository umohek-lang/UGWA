from django import forms

from .models import DuesType, DuesSchedule
from django.contrib.auth import get_user_model

User = get_user_model()

class DuesTypeForm(forms.ModelForm):

    class Meta:
        model = DuesType

        fields = [
            "name",
            "description",
            "amount",
            "frequency",
            "is_active",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Monthly Membership Dues",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Describe this dues type..."
                    ),
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "0.00",
                }
            ),

            "frequency": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class DuesScheduleForm(forms.ModelForm):

    class Meta:
        model = DuesSchedule

        fields = [
            "member",
            "dues_type",
            "amount",
            # "frequency",
            "start_date",
            "next_due_date",
            "end_date",
            "is_active",
        ]

        widgets = {

            "member": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "dues_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "frequency": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "next_due_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "end_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["member"].queryset = (
            self.fields["member"]
            .queryset
            .filter(
                membership_code__isnull=False
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        )



class MemberEditForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "membership_status",
            "membership_date",
            "photo",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "membership_status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "membership_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "photo": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }