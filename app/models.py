import logging.config
from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from dateutil.relativedelta import relativedelta
import logging
from decimal import Decimal


User = get_user_model()


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Plan(models.Model):
    DURATION_UNITS = (
        ("DAYS", "Days"),
        ("WEEKS", "Weeks"),
        ("MONTHS", "Months"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    daily_profit_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    min_amount = models.DecimalField(max_digits=15, decimal_places=2)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_value = models.PositiveIntegerField()
    duration_unit = models.CharField(
        max_length=6, choices=DURATION_UNITS, default="Days"
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.duration_value} {self.get_duration_unit_display()})"

    def get_duration_in_days(self):
        """Convert duration to days for calculations"""
        conversion = {
            "DAYS": 1,
            "WEEKS": 7,
            "MONTHS": 30,  # Approximation for month duration
        }
        return self.duration_value * conversion[self.duration_unit]

    @property
    def total_return(self):
        """Returns the total return in % over the duration."""
        return self.daily_profit_percentage * self.get_duration_in_days()

    @property
    def daily_return(self):
        return self.daily_profit_percentage


class Mining(models.Model):
    DURATION_UNITS = (
        ("DAYS", "Days"),
        ("WEEKS", "Weeks"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    return_profit = models.DecimalField(max_digits=5, decimal_places=2)
    min_amount = models.DecimalField(max_digits=15, decimal_places=2)
    max_amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_value = models.PositiveIntegerField()
    duration_unit = models.CharField(
        max_length=6, choices=DURATION_UNITS, default="Days"
    )
    description = models.TextField(blank=True)
    features = models.JSONField(default=list)

    def __str__(self):
        return f"{self.name} ({self.duration_value} {self.get_duration_unit_display()})"

    def get_duration_in_days(self):
        """Convert duration to days for calculations"""
        conversion = {
            "DAYS": 1,
            "WEEKS": 7,
        }
        return self.duration_value * conversion[self.duration_unit]


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    WALLET_TYPES = (
        ("DEPOSIT", "Deposit Wallet"),
        ("INTEREST", "Interest Wallet"),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    wallet_type = models.CharField(max_length=8, choices=WALLET_TYPES)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "wallet_type")

    def __str__(self):
        return f"{self.get_wallet_type_display()} {self.balance}"


class Investment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True)
    profit_accumulated = models.DecimalField(
        max_digits=20, decimal_places=2, default=0.00
    )  # New field
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        logging.debug("Start Here!!")
        logging.debug("Primary Key: {}".format(self.pk))
        if self._state.adding:
            start_date = timezone.now()
            logging.info("Start Date: {}".format(start_date))
            if self.plan.duration_unit == "MONTHS":
                self.end_date = start_date + relativedelta(
                    months=+self.plan.duration_value
                )
            else:
                days = self.plan.get_duration_in_days()
                logging.info("Days: {}".format(days))
                self.end_date = start_date + timedelta(days=days)
        logging.debug("Saved Here!!")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    @property
    def current_profit(self):
        if not self.is_active:
            return self.profit_accumulated
        # Calculate based on days passed and daily % return
        now = timezone.now()
        elapsed_days = (now - self.start_date).days
        daily_profit = self.amount * (self.plan.daily_profit_percentage / 100)
        return round(
            min(elapsed_days, self.plan.get_duration_in_days()) * daily_profit, 2
        )

    @property
    def progress_percentage(self):
        total_days = self.plan.get_duration_in_days()
        elapsed_days = (timezone.now() - self.start_date).days
        return min(int((elapsed_days / total_days) * 100), 100)


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    TRANSACTION_TYPES = (
        ("INVESTMENT", "Investment"),
        ("PROFIT", "Profit"),
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdraw"),
    )
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    investment = models.ForeignKey(
        Investment, on_delete=models.SET_NULL, null=True, blank=True
    )
    # This field will store the wallet (deposit or interest) from which funds are withdrawn.
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    # For deposits, this stores the deposit method; for withdrawals, it may store the chosen crypto method.
    deposit_method = models.ForeignKey(
        "DepositMethod", on_delete=models.SET_NULL, null=True, blank=True
    )
    # New field: stores the external wallet address for withdrawals.
    withdrawal_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    admin_note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class DepositMethod(models.Model):
    CRYPTO_CHOICES = (
        ("BANK", "Bank"),
        ("BTC", "Bitcoin"),
        ("ETH", "Ethereum"),
        ("USDT", "Tether"),
        ("DOD", "Dodge"),
        ("LTC", "Litecoin"),
    )

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    crypto_type = models.CharField(max_length=4, choices=CRYPTO_CHOICES, unique=True)
    wallet_address = models.CharField(max_length=255, null=True, blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    instruction = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        """Automatically set instructions based on deposit type."""
        if self.crypto_type == "BANK":
            self.instruction = (
                "1. Transfer the deposit amount to the provided bank account details.\n"
                "2. Use your registered account number or username as the payment reference.\n"
                "3. After making the transfer, upload the transaction receipt for verification.\n"
                "4. Your deposit will be processed and credited to your account after confirmation."
            )
            self.wallet_address = None  # No wallet address for bank deposits
            self.qr_code = None  # No QR code for bank deposits
        elif not self.instruction:
            self.instruction = (
                "Use the provided wallet address or scan the QR code to deposit."
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_crypto_type_display()

    def display_wallet_info(self):
        """Return wallet info for crypto deposits only."""
        if self.crypto_type != "BANK":
            return f"Wallet Address: {self.wallet_address}, QR Code: {self.qr_code.url if self.qr_code else 'N/A'}"
        return "Bank transfer method does not use a wallet address or QR code."


SIGN_ON_BONUS_AMOUNT = Decimal("10.00")  # Set your bonus amount here


# Auto create wallets when user is created
@receiver(post_save, sender=User)
def create_user_wallets(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:  # Combine checks
        # Create or get wallets
        deposit_wallet, _ = Wallet.objects.get_or_create(
            user=instance, wallet_type="DEPOSIT"
        )
        interest_wallet, created_interest_wallet = Wallet.objects.get_or_create(
            user=instance, wallet_type="INTEREST"
        )
        if created_interest_wallet:  # Ensure bonus is only given once
            # Add sign-on bonus to interest wallet
            interest_wallet.balance += SIGN_ON_BONUS_AMOUNT
            interest_wallet.save()

            # Create a transaction record for the bonus
            Transaction.objects.create(
                user=instance,
                wallet=interest_wallet,
                amount=SIGN_ON_BONUS_AMOUNT,
                transaction_type="PROFIT",  # Or create a new type like "BONUS"
                status="APPROVED",
                admin_note="Sign-on bonus for new user",
            )
