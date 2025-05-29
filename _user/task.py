from django.utils import timezone
from decimal import Decimal
from app.models import Investment, Wallet, Transaction


def process_daily_profits():
    today = timezone.now().date()
    investments = Investment.objects.filter(is_active=True)

    for investment in investments:
        # Check if investment is still valid
        if investment.end_date < timezone.now():
            investment.is_active = False
            investment.save()
            continue

        elapsed_days = (timezone.now().date() - investment.start_date.date()).days
        total_days = investment.plan.get_duration_in_days()

        # Check if profit has already been credited for today
        already_credited = Transaction.objects.filter(
            user=investment.user,
            investment=investment,
            transaction_type="PROFIT",
            timestamp__date=today,
        ).exists()

        if already_credited:
            continue  # Skip if today's profit already credited

        if elapsed_days <= total_days:
            # Calculate daily profit
            daily_profit = investment.amount * (
                investment.plan.daily_profit_percentage / Decimal("100.0")
            )

            # Get user's interest wallet
            interest_wallet = Wallet.objects.get(
                user=investment.user, wallet_type="INTEREST"
            )
            interest_wallet.balance += daily_profit
            interest_wallet.save()

            # Log transaction
            Transaction.objects.create(
                user=investment.user,
                investment=investment,
                wallet=interest_wallet,
                amount=daily_profit,
                transaction_type="PROFIT",
                status="APPROVED",
                admin_note=f"Daily profit for {investment.plan.name}",
            )

            # Update investment profit_accumulated
            investment.profit_accumulated += daily_profit
            investment.save()
