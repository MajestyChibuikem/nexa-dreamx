from django.contrib import admin
from .models import Plan, Wallet, Investment, Transaction, DepositMethod
from django import forms


class PlanAdminForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = "__all__"
        widgets = {
            "duration_value": forms.NumberInput(),
            "duration_unit": forms.Select(),
        }


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    form = PlanAdminForm
    list_display = (
        "name",
        "daily_profit_percentage",
        "duration_display",
        "min_amount",
        "max_amount",
    )

    def duration_display(self, obj):
        return f"{obj.duration_value} {obj.get_duration_unit_display()}"

    duration_display.short_description = "Duration"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "wallet_type", "balance", "created_at")
    search_fields = ("user__email", "wallet_type")
    list_filter = ("wallet_type", "created_at")


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "wallet",
        "amount",
        "start_date",
        "end_date",
        "is_active",
    )
    search_fields = ("user__email", "plan__name")
    list_filter = ("is_active", "start_date", "end_date")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "investment",
        "wallet",
        "amount",
        "transaction_type",
        "status",
        "timestamp",
    )
    search_fields = ("user__email", "transaction_type", "status")
    list_filter = ("transaction_type", "status", "timestamp")


@admin.register(DepositMethod)
class DepositMethodAdmin(admin.ModelAdmin):
    list_display = ("crypto_type", "wallet_address", "is_active")
    search_fields = ("crypto_type", "wallet_address")
    list_filter = ("crypto_type", "is_active")
