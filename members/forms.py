from django import forms

from .models import MemberProfile


class MemberProfileForm(forms.ModelForm):

    class Meta:

        model = MemberProfile

        fields = (
            "profile_photo",
            "gender",
            "date_of_birth",
            "address",
            "city",
            "state",
            "lga",
            "occupation",
            "organization",
            "qualification",
            "membership_category",
            "branch",
        )

        widgets = {

            "profile_photo": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Residential address",
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "City",
                }
            ),

            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "State",
                }
            ),

            "lga": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Local Government Area",
                }
            ),

            "occupation": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Occupation",
                }
            ),

            "organization": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Organization",
                }
            ),

            "qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Highest qualification",
                }
            ),

            "membership_category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "branch": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "membership_category"
        ].queryset = self.fields[
            "membership_category"
        ].queryset.filter(
            is_active=True
        )

        self.fields[
            "branch"
        ].queryset = self.fields[
            "branch"
        ].queryset.filter(
            is_active=True
        )