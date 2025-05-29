from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from users.models import CustomUser
from app.models import Plan, DepositMethod


class CustomUserLoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Plan name",
                }
            ),
            "daily_profit_percentage": forms.NumberInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Daily Profit Percentage",
                }
            ),
            "min_amount": forms.NumberInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Minimum Amount",
                }
            ),
            "max_amount": forms.NumberInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Maximum Amount",
                }
            ),
            "duration_value": forms.NumberInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Duration Value (e.g. 30)",
                }
            ),
            "duration_unit": forms.Select(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Describe the plan",
                    "rows": 5,
                }
            ),
        }


class DepositMethodForm(forms.ModelForm):
    class Meta:
        model = DepositMethod
        fields = "__all__"
        widgets = {
            "crypto_type": forms.Select(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                }
            ),
            "wallet_address": forms.TextInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Wallet Address",
                }
            ),
            "qr_code": forms.FileInput(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                }
            ),
            "is_active": forms.CheckboxInput(attrs={}),
            "instruction": forms.Textarea(
                attrs={
                    "class": "w-full border border-gray-500 px-3 py-2 rounded-sm text-sm font-medium outline-none text-black",
                    "placeholder": "Instructions",
                    "rows": 5,
                }
            ),
        }


class TransactionActionForm(forms.Form):
    admin_note = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}), required=False, label="Admin Note"
    )
