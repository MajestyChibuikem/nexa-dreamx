from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import Referral

User = get_user_model()


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name", required=True)
    last_name = forms.CharField(max_length=30, label="Last Name", required=True)
    mobile = forms.CharField(max_length=15, label="Mobile", required=True)
    username = forms.CharField(max_length=15, label="Username", required=True)
    password1 = forms.CharField(
        max_length=128, label="Password", required=True, widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        max_length=128,
        label="Confirm Password",
        required=True,
        widget=forms.PasswordInput(),
    )
    # Hidden referral code field
    referral_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean_mobile(self):
        mobile = self.cleaned_data["mobile"]
        if User.objects.filter(mobile=mobile).exists():
            raise ValidationError("A user with this mobile number already exists.")
        return mobile

    def save(self, request):
        # 1) Create user via allauth
        user = super(CustomSignupForm, self).save(request)

        # 2) Populate custom fields
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.mobile = self.cleaned_data.get("mobile")
        user.username = self.cleaned_data.get("username")

        # 3) Handle referral logic
        code = self.cleaned_data.get("referral_code")
        if code:
            try:
                referrer = User.objects.get(username=code)
            except User.DoesNotExist:
                referrer = None

            if referrer:
                user.referred_by = referrer
                # Save all updated fields in one go
                user.save(
                    update_fields=[
                        "first_name",
                        "last_name",
                        "mobile",
                        "username",
                        "referred_by",
                    ]
                )
                # Create referral record
                Referral.objects.create(referrer=referrer, referred=user)
            else:
                # Save custom fields if no valid referrer
                user.save(
                    update_fields=["first_name", "last_name", "mobile", "username"]
                )
        else:
            # No referral code
            user.save(update_fields=["first_name", "last_name", "mobile", "username"])

        return user
