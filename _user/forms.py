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
    crypto_type = forms.ChoiceField(
        choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('USDT', 'Tether')],
        widget=forms.HiddenInput()
    )
    amount = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'w-full pl-4 pr-16 py-3 form-input rounded-lg text-white focus:outline-none transition-all duration-300',
            'placeholder': '0.00'
        })
    )
    destination_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-4 pr-12 py-3 form-input rounded-lg text-white focus:outline-none transition-all duration-300 address-input',
            'placeholder': 'Enter wallet address'
        })
    )
    network = forms.ChoiceField(
        choices=[('MAINNET', 'Main Network'), ('TESTNET', 'Test Network')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 form-select rounded-lg text-white focus:outline-none transition-all duration-300'
        })
    )
    address_label = forms.CharField(
        required=False, 
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 form-input rounded-lg text-white focus:outline-none transition-all duration-300',
            'placeholder': 'Optional label for your reference'
        })
    )
    priority = forms.ChoiceField(
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 form-select rounded-lg text-white focus:outline-none transition-all duration-300'
        })
    )
    two_factor_code = forms.CharField(
        max_length=6, 
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 form-input rounded-lg text-white focus:outline-none transition-all duration-300',
            'placeholder': '6-digit 2FA code'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 form-input rounded-lg text-white focus:outline-none transition-all duration-300',
            'placeholder': 'Your account password'
        })
    )
    confirmation = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2'
        })
    )

    def __init__(self, user=None, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(**kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        if not self.user:
            raise ValidationError("User not found")
            
        # Verify password
        password = cleaned_data.get('password')
        if password:
            from django.contrib.auth import authenticate
            if not authenticate(username=self.user.username, password=password):
                raise ValidationError("Incorrect password")
            
        # Check available balance
        amount = cleaned_data.get('amount')
        if amount:
            try:
                wallet = Wallet.objects.get(user=self.user, wallet_type="INTEREST")
                if not wallet.can_withdraw(amount):
                    raise ValidationError(
                        f"Insufficient available balance. You have ${wallet.available_balance} available."
                    )
            except Wallet.DoesNotExist:
                raise ValidationError("Wallet not found")
                
        return cleaned_data
