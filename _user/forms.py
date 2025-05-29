from django import forms
from users.models import CustomUser
from app.models import Investment, DepositMethod, Wallet
from django.core.exceptions import ValidationError


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "username",
            "country",
            "address",
            "state",
            "zip_code",
            "city",
            "profile_photo",
        ]
        widgets = {
            "first_name": forms.TextInput(),
            "last_name": forms.TextInput(),
            "email": forms.EmailInput(),
            "username": forms.TextInput(),
            "mobile": forms.TextInput(),
            "country": forms.TextInput(),
            "address": forms.TextInput(),
            "state": forms.TextInput(),
            "zip_code": forms.TextInput(),
            "city": forms.TextInput(),
        }


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ["plan", "wallet", "amount"]
        widgets = {"plan": forms.HiddenInput()}

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        if user:
            self.fields["wallet"].queryset = user.wallet_set.all()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        plan = self.cleaned_data.get("plan")

        if plan and (amount < plan.min_amount or amount > plan.max_amount):
            raise forms.ValidationError(
                f"Amount must be between {plan.min_amount} and {plan.max_amount}"
            )
        return amount

    def clean(self):
        cleaned_data = super().clean()
        wallet = cleaned_data.get("wallet")
        amount = cleaned_data.get("amount")

        if wallet and amount and wallet.balance < amount:
            raise forms.ValidationError("Insufficient balance in the selected wallet.")
        return cleaned_data


class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2)


class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2)
    wallet_address = forms.CharField(max_length=255)

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.user = user

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        interest_wallet = Wallet.objects.get(user=self.user, wallet_type="INTEREST")
        if amount > interest_wallet.balance:
            raise ValidationError("Insufficient balance in interest wallet")
        return amount
