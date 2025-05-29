from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
    TemplateView,
)
from app.models import Investment, Wallet, Transaction, DepositMethod, Plan, Mining
from users.models import CustomUser
from .forms import (
    CustomUserLoginForm,
    PlanForm,
    DepositMethodForm,
    TransactionActionForm,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone


template_url = "dashboard/admin"


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class DashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = f"{template_url}/index.html"


class UserListView(ListView):
    model = CustomUser
    template_name = f"{template_url}/users/user_list.html"
    context_object_name = "users"


class UserDetailView(DetailView):
    model = CustomUser
    template_name = f"{template_url}/users/user_detail.html"
    context_object_name = "user"


class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = f"{template_url}/users/user_confirm_delete.html"
    success_url = reverse_lazy("admin:user-list")


class PlanListView(ListView):
    model = Plan
    template_name = f"{template_url}/plans/plan_list.html"
    context_object_name = "plans"


# Detail View
class PlanDetailView(DetailView):
    model = Plan
    template_name = f"{template_url}/plans/plan_detail.html"
    context_object_name = "plan"


# Create View
class PlanCreateView(CreateView):
    model = Plan
    template_name = f"{template_url}/plans/plan_form.html"
    form_class = PlanForm
    success_url = reverse_lazy("admin:plan-list")


# Update View
class PlanUpdateView(UpdateView):
    model = Plan
    template_name = f"{template_url}/plans/plan_form.html"
    form_class = PlanForm
    success_url = reverse_lazy("admin:plan-list")


# Delete View
class PlanDeleteView(DeleteView):
    model = Plan
    template_name = f"{template_url}/plans/plan_confirm_delete.html"
    success_url = reverse_lazy("admin:plan-list")


class InvestmentListView(ListView):
    model = Investment
    template_name = f"{template_url}/investment/investment_list.html"
    context_object_name = "investments"


class InvestmentDetailView(DetailView):
    model = Investment
    template_name = f"{template_url}/investment/investment_detail.html"
    context_object_name = "investment"


class InvestmentCreateView(CreateView):
    model = Investment
    template_name = f"{template_url}/investment/investment_form.html"
    fields = "__all__"
    success_url = reverse_lazy("investment-list")


class InvestmentUpdateView(UpdateView):
    model = Investment
    template_name = f"{template_url}/investment/investment_form.html"
    fields = "__all__"
    success_url = reverse_lazy("investment-list")


class InvestmentDeleteView(DeleteView):
    model = Investment
    template_name = f"{template_url}/investment_confirm_delete.html"
    success_url = reverse_lazy("investment-list")


class WalletListView(ListView):
    model = Wallet
    template_name = f"{template_url}/wallet/wallet_list.html"
    context_object_name = "wallets"


class WalletDetailView(DetailView):
    model = Wallet
    template_name = f"{template_url}/wallet/wallet_detail.html"
    context_object_name = "wallet"


class WalletCreateView(CreateView):
    model = Wallet
    template_name = f"{template_url}/wallet/wallet_form.html"
    fields = "__all__"
    success_url = reverse_lazy("wallet-list")


class WalletUpdateView(UpdateView):
    model = Wallet
    template_name = f"{template_url}/wallet/wallet_form.html"
    fields = "__all__"
    success_url = reverse_lazy("wallet-list")


class WalletDeleteView(DeleteView):
    model = Wallet
    template_name = f"{template_url}/wallet/wallet_confirm_delete.html"
    success_url = reverse_lazy("wallet-list")


class MiningListView(ListView):
    model = Mining
    template_name = f"{template_url}/mining.html"
    context_object_name = "mining"


class MiningDetailView(DetailView):
    model = Mining
    template_name = f"{template_url}/mining_detail.html"
    context_object_name = "mining"


class MiningCreateView(CreateView):
    model = Mining
    template_name = f"{template_url}/mining_form.html"
    fields = "__all__"
    success_url = reverse_lazy("mining-list")


class MiningUpdateView(UpdateView):
    model = Mining
    template_name = f"{template_url}/mining_form.html"
    fields = "__all__"
    success_url = reverse_lazy("mining-list")


class MiningDeleteView(DeleteView):
    model = Mining
    template_name = f"{template_url}/mining_confirm_delete.html"
    success_url = reverse_lazy("mining-list")


class TransactionListView(ListView):
    model = Transaction
    template_name = f"{template_url}/transactions/transaction_list.html"
    context_object_name = "transactions"


class TransactionDetailView(DetailView):
    model = Transaction
    template_name = f"{template_url}/transactions/transaction_detail.html"
    context_object_name = "transaction"


class TransactionActionView(UserPassesTestMixin, FormView):
    template_name = f"{template_url}/transactions/transaction_action.html"
    form_class = TransactionActionForm
    success_url = reverse_lazy("admin:transaction-list")

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transaction"] = get_object_or_404(Transaction, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        transaction = get_object_or_404(Transaction, pk=self.kwargs["pk"])
        wallet = get_object_or_404(Wallet, user=transaction.user, wallet_type="DEPOSIT")
        action = self.request.POST.get("action")
        admin_note = form.cleaned_data["admin_note"]

        if action not in ["approve", "reject"]:
            form.add_error(None, "Invalid action.")
            return self.form_invalid(form)

        # Set transaction status
        transaction.status = "APPROVED" if action == "approve" else "REJECTED"
        transaction.admin_note = admin_note
        transaction.save()

        # Process balance only if approved
        if transaction.status == "APPROVED":
            if not wallet:
                form.add_error(None, "Transaction has no associated wallet.")
                return self.form_invalid(form)

            amount = transaction.amount
            if transaction.transaction_type == "DEPOSIT":
                wallet.balance += amount
            elif transaction.transaction_type == "WITHDRAW":
                if wallet.balance < amount:
                    form.add_error(None, "Insufficient funds in wallet for withdrawal.")
                    transaction.status = "REJECTED"
                    transaction.save()
                    return self.form_invalid(form)
                wallet.balance -= amount

            wallet.save()

            # Send approval email
            subject = "Transaction Approved"
            recipient_email = transaction.user.email
            # Inside your form_valid method
            context = {
                "user": transaction.user,
                "transaction": transaction,
                "wallet": wallet,
                "now": timezone.now(),  # Add this line
            }
            message = render_to_string("emails/transaction_approved.html", context)
            email = EmailMessage(subject, message, to=[recipient_email])
            email.content_subtype = "html"
            email.send()

        messages.success(
            self.request,
            f"Transaction {transaction.id} has been {transaction.status.lower()}.",
        )
        return super().form_valid(form)


class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = f"{template_url}/transactions/transaction_confirm_delete.html"
    success_url = reverse_lazy("transaction-list")


class DepositMethodListView(ListView):
    model = DepositMethod
    template_name = f"{template_url}/deposit_methods/deposit_method_list.html"
    context_object_name = "deposit_methods"


class DepositMethodDetailView(DetailView):
    model = DepositMethod
    template_name = f"{template_url}/deposit_methods/deposit_method_detail.html"
    context_object_name = "deposit_method"


class DepositMethodCreateView(CreateView):
    model = DepositMethod
    template_name = f"{template_url}/deposit_methods/deposit_method_form.html"
    form_class = DepositMethodForm
    success_url = reverse_lazy("admin:deposit-method-list")


class DepositMethodUpdateView(UpdateView):
    model = DepositMethod
    template_name = f"{template_url}/deposit_methods/deposit_method_form.html"
    form_class = DepositMethodForm
    success_url = reverse_lazy("admin:deposit-method-list")


class DepositMethodDeleteView(DeleteView):
    model = DepositMethod
    template_name = f"{template_url}/deposit_methods/deposit_method_confirm_delete.html"
    success_url = reverse_lazy("admin:deposit-method-list")


class LoginView(FormView):
    form_class = CustomUserLoginForm
    template_name = "account/admin_login.html"
    success_url = reverse_lazy("admin:dashboard")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, username=username, password=password)
        if user is not None and user.is_superuser or user.is_staff:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, "Invalid credentials or not authorized")
            return super().form_valid(form)
