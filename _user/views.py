import logging.config
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    TemplateView,
    ListView,
    UpdateView,
    CreateView,
    DetailView,
)
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Plan, Investment, Transaction, DepositMethod, Wallet
from .forms import ProfileUpdateForm, InvestmentForm, DepositForm, WithdrawalForm
from users.models import CustomUser, Referral
import logging
from django.db.models import Sum
import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

template_dir = "dashboard/user"


def send_transaction_email(template_name, subject, context, to_email):
    html_content = render_to_string(f"emails/{template_name}", context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[to_email],
        reply_to=[settings.SUPPORT_EMAIL],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = f"{template_dir}/index.html"

    def get_user_wallet(self, wallet_type):
        """Helper method to fetch user wallet efficiently."""
        return Wallet.objects.filter(
            user=self.request.user, wallet_type=wallet_type
        ).first()

    def get_transaction_sum(self, transaction_type, status=None):
        """Helper method to sum transactions efficiently."""
        filters = {"user": self.request.user, "transaction_type": transaction_type}
        if status:
            filters["status"] = status
        return (
            Transaction.objects.filter(**filters).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

    def get_context_data(self, **kwargs):
        """Fetch and structure dashboard data efficiently."""
        context = super().get_context_data(**kwargs)

        # Wallets
        context["deposit_wallet"] = self.get_user_wallet("DEPOSIT")
        context["interest_wallet"] = self.get_user_wallet("INTEREST")

        # Transactions
        context["transactions"] = Transaction.objects.filter(
            user=self.request.user
        ).select_related("wallet")

        # Optimized total calculations
        context["total_deposits"] = self.get_transaction_sum("DEPOSIT", "APPROVED")
        context["total_withdrawals"] = self.get_transaction_sum("WITHDRAW", "APPROVED")
        context["total_investment"] = self.get_transaction_sum("INVESTMENT")

        # Investments
        context["investments"] = Investment.objects.filter(user=self.request.user)

        context["REFERRAL_LINK"] = (
            os.getenv("APP_URL") + f"/accounts/signup/?ref={self.request.user.username}"
        )

        context["total_referrals"] = Referral.objects.filter(
            referrer=self.request.user
        ).count()

        return context


class PlanListView(LoginRequiredMixin, ListView):
    model = Plan
    template_name = f"{template_dir}/plan-list.html"
    context_object_name = "plans"


class InvestmentCreateView(LoginRequiredMixin, CreateView):
    model = Investment
    form_class = InvestmentForm
    template_name = f"{template_dir}/investment_create.html"
    success_url = reverse_lazy("user:investments")

    def get_initial(self):
        initial = super().get_initial()
        plan_id = self.kwargs["pk"]
        initial["plan"] = get_object_or_404(Plan, id=plan_id)
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        # Add the plan name to the context
        context = super().get_context_data(**kwargs)
        plan_id = self.kwargs["pk"]
        plan = get_object_or_404(Plan, id=plan_id)
        context["plan"] = plan
        return context

    def form_valid(self, form):
        # Deduct amount from wallet
        wallet = form.cleaned_data["wallet"]
        amount = form.cleaned_data["amount"]

        # Create investment
        investment = form.save(commit=False)
        investment.user = self.request.user
        investment.save()

        wallet.balance -= amount
        wallet.save()

        # Log transaction
        Transaction.objects.create(
            user=self.request.user,
            investment=investment,
            wallet=wallet,
            amount=amount,
            transaction_type="INVESTMENT",
        )

        # Calculate expected return
        # Calculate total interest based on daily percentage and total days
        days = investment.plan.get_duration_in_days()
        interest_rate = float(investment.plan.daily_profit_percentage) * days
        expected_return = float(amount) * (1 + interest_rate / 100)

        # Send HTML email
        context = {
            "user": self.request.user,
            "investment": investment,
            "expected_return": expected_return,
            "site_name": "Your Investment Platform",
        }

        send_transaction_email(
            "investment_confirmation.html",
            f"Investment Confirmation - {investment.plan.name}",
            context,
            self.request.user.email,
        )

        return super().form_valid(form)


class InvestmentListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = f"{template_dir}/investments.html"
    context_object_name = "investments"

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, transaction_type="INVESTMENT"
        ).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = Wallet.objects.filter(user=self.request.user).get(
            wallet_type="DEPOSIT"
        )
        return context


class DepositListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = f"{template_dir}/deposits.html"
    context_object_name = "deposits"

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, transaction_type="DEPOSIT"
        ).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = Wallet.objects.filter(
            user=self.request.user, wallet_type="DEPOSIT"
        ).first()
        return context


class DepositMethodListView(LoginRequiredMixin, ListView):
    model = DepositMethod
    template_name = f"{template_dir}/deposit_methods.html"
    context_object_name = "deposits"

    def get_queryset(self):
        return DepositMethod.objects.filter(is_active=True)


class DepositCreateView(LoginRequiredMixin, FormView):
    form_class = DepositForm
    template_name = f"{template_dir}/deposit_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crypto_id = self.kwargs["pk"]
        deposit_method = get_object_or_404(DepositMethod, id=crypto_id)
        context["deposit_method"] = deposit_method
        return context

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        crypto_id = self.kwargs["pk"]
        deposit_method = get_object_or_404(DepositMethod, id=crypto_id)

        # Create the transaction and save it to access the PK
        transaction = Transaction.objects.create(
            user=self.request.user,
            amount=amount,
            transaction_type="DEPOSIT",
            deposit_method=deposit_method,
            status="PENDING",
        )

        context = {
            "user": self.request.user,
            "amount": amount,
            "deposit_method": deposit_method,
            "transaction": transaction,
            "site_name": "Your Investment Platform",
        }

        send_transaction_email(
            "deposit_pending.html",
            f"Deposit Request Received - #{transaction.id}",
            context,
            self.request.user.email,
        )

        # Add to both views after sending user email
        admin_context = {
            "user": self.request.user,
            "transaction": transaction,
            "amount": amount,
            "type": "Deposit" if isinstance(self, DepositCreateView) else "Withdrawal",
        }

        send_transaction_email(
            "admin_notification.html",
            f"New {admin_context['type']} Request - #{transaction.id}",
            admin_context,
            settings.ADMIN_EMAIL,
        )

        self.transaction_pk = transaction.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("user:deposit_details", kwargs={"pk": self.transaction_pk})


class WithdrawalMethodListView(LoginRequiredMixin, ListView):
    model = DepositMethod
    template_name = f"{template_dir}/withdrawals_methods.html"
    context_object_name = "cryptos"

    def get_queryset(self):
        return DepositMethod.objects.filter(is_active=True).exclude(crypto_type="BANK")


class WithdrawalCreateView(LoginRequiredMixin, FormView):
    form_class = WithdrawalForm
    template_name = (
        f"{template_dir}/withdrawal_create.html"  # Ensure template path is correct
    )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crypto_id = self.kwargs["pk"]
        deposit_method = get_object_or_404(DepositMethod, id=crypto_id)
        interest_wallet = get_object_or_404(
            Wallet, user=self.request.user, wallet_type="INTEREST"
        )
        context["deposit_method"] = deposit_method
        context["interest_wallet"] = interest_wallet
        return context

    def form_valid(self, form):
        amount = form.cleaned_data["amount"]
        wallet_address = form.cleaned_data["wallet_address"]

        # Retrieve the crypto method from the URL pk
        crypto_pk = self.kwargs["pk"]
        crypto_method = get_object_or_404(DepositMethod, pk=crypto_pk)

        # Retrieve the wallet from which the withdrawal will be made
        interest_wallet = Wallet.objects.get(
            user=self.request.user, wallet_type="INTEREST"
        )

        # Create the transaction, storing the interest wallet, external withdrawal address,
        # and the chosen crypto method.
        transaction = Transaction.objects.create(
            user=self.request.user,
            wallet=interest_wallet,  # The wallet being withdrawn from
            withdrawal_address=wallet_address,  # The external wallet address for withdrawal
            amount=amount,
            transaction_type="WITHDRAW",
            deposit_method=crypto_method,  # Using deposit_method field to store crypto method
            status="PENDING",
        )

        # Prepare email context
        context = {
            "user": self.request.user,
            "amount": amount,
            "wallet_address": wallet_address,
            "crypto_method": crypto_method,
            "transaction": transaction,
            "site_name": "Your Investment Platform",
        }

        send_transaction_email(
            "withdrawal_pending.html",
            f"Withdrawal Request Received - #{transaction.id}",
            context,
            self.request.user.email,
        )

        # Add to both views after sending user email
        admin_context = {
            "user": self.request.user,
            "transaction": transaction,
            "amount": amount,
            "type": "Deposit" if isinstance(self, DepositCreateView) else "Withdrawal",
        }

        send_transaction_email(
            "admin_notification.html",
            f"New {admin_context['type']} Request - #{transaction.id}",
            admin_context,
            settings.ADMIN_EMAIL,
        )

        self.transaction_pk = transaction.pk
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("user:withdrawal_details", kwargs={"pk": self.transaction_pk})


class WithdrawalListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = f"{template_dir}/withdrawals.html"
    context_object_name = "withdrawals"

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, transaction_type="WITHDRAW"
        ).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = Wallet.objects.filter(
            user=self.request.user, wallet_type="DEPOSIT"
        ).first()
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = f"{template_dir}/transaction_pending.html"
    context_object_name = "transaction"

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class InterestListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = f"{template_dir}/interests.html"
    context_object_name = "interests"

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user, transaction_type="PROFIT"
        ).order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wallet"] = Wallet.objects.filter(
            user=self.request.user, wallet_type="DEPOSIT"
        ).first()
        return context


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    model = CustomUser
    template_name = f"{template_dir}/profile.html"
    success_url = reverse_lazy("user:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_invalid(self, form):
        print(form.errors)  # This will show which field caused the error in the console
        return super().form_invalid(form)
