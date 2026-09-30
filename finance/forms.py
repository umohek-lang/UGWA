from django import forms

from .models import Income, Expense


class IncomeForm(forms.ModelForm):

    class Meta:

        model = Income

        fields = [
            "category",
            "amount",
            "transaction_date",
            "payment_method",
            "reference",
            "description",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "transaction_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Payment reference",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter details about this income..."
                    ),
                }
            ),
        }


class ExpenseForm(forms.ModelForm):

    class Meta:

        model = Expense

        fields = [
            "category",
            "amount",
            "transaction_date",
            "payment_method",
            "reference",
            "payee",
            "description",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "transaction_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "payment_method": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Payment reference",
                }
            ),

            "payee": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Person or organization paid",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "Enter details about this expense..."
                    ),
                }
            ),
        }
