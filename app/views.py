from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Plan, Wallet, Transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .forms import WithdrawalForm

# Create your views here.
class HomeView(ListView):
    model = Plan
    template_name = "public/index.html"
    context_object_name = "plans"


class AboutView(TemplateView):
    template_name = "public/about.html"


class ContactView(TemplateView):
    template_name = "public/contact.html"


class ServicesView(TemplateView):
    template_name = "public/services.html"


class PlanListView(ListView):
    model = Plan
    template_name = "public/plan-list.html"
    context_object_name = "plans"


def custom_error_404(request, e):
    return render(request, "errors/404.html", status=404)


def custom_error_500(request):
    return render(request, "errors/500.html", status=500)


class WithdrawalView(LoginRequiredMixin, FormView):
    template_name = 'user/withdrawal_methods.html'
    form_class = WithdrawalForm
    success_url = reverse_lazy('user:withdrawals')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'available_cryptos': self.get_available_cryptos(user),
            'min_withdrawal_amount': Decimal('10.00'),  # Set your minimum
            'network_fee': Decimal('0.0005'),  # Example fee
            'processing_fee': Decimal('1.00'),  # Example fee
        })
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = self.request.user
                amount = form.cleaned_data['amount']
                crypto_type = form.cleaned_data['crypto_type']
                wallet_address = form.cleaned_data['destination_address']
                
                # Get the appropriate wallet (INTEREST wallet for withdrawals)
                wallet = Wallet.objects.get(user=user, wallet_type="INTEREST")
                
                if not wallet.can_withdraw(amount):
                    messages.error(self.request, "Insufficient available balance")
                    return self.form_invalid(form)
                
                # Create the withdrawal transaction
                withdrawal = Transaction.objects.create(
                    user=user,
                    wallet=wallet,
                    amount=amount,
                    transaction_type="WITHDRAW",
                    withdrawal_address=wallet_address,
                    status="PENDING",
                    admin_note=f"Pending {crypto_type} withdrawal to {wallet_address}"
                )
                
                messages.success(
                    self.request,
                    f"Withdrawal request for ${amount} submitted successfully. "
                    "It will be processed shortly."
                )
                
                # Here you would typically:
                # 1. Send email confirmation
                # 2. Notify admin
                # 3. Queue for processing (if using Celery)
                
        except Exception as e:
            messages.error(self.request, f"Withdrawal failed: {str(e)}")
            return self.form_invalid(form)
            
        return super().form_valid(form)
    
    def get_available_cryptos(self, user):
        """Returns available crypto balances for the user"""
        interest_wallet = Wallet.objects.get(user=user, wallet_type="INTEREST")
        return [
            {
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'balance': interest_wallet.balance / Decimal('50000'),  # Example conversion
                'usd_value': interest_wallet.balance,
                'network': 'Bitcoin Network'
            },
            # Add other cryptocurrencies...
        ]