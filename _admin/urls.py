from django.urls import path
from .views import (
    LoginView,
    DashboardView,
    UserListView,
    UserDetailView,
    UserDeleteView,
    InvestmentListView,
    InvestmentDetailView,
    InvestmentCreateView,
    InvestmentUpdateView,
    InvestmentDeleteView,
    WalletListView,
    WalletDetailView,
    WalletCreateView,
    WalletUpdateView,
    WalletDeleteView,
    TransactionListView,
    TransactionDetailView,
    TransactionActionView,
    TransactionDeleteView,
    DepositMethodListView,
    DepositMethodDetailView,
    DepositMethodCreateView,
    DepositMethodUpdateView,
    DepositMethodDeleteView,
    PlanCreateView,
    PlanDeleteView,
    PlanDetailView,
    PlanUpdateView,
    PlanListView,
    MiningCreateView,
    MiningDeleteView,
    MiningDetailView,
    MiningUpdateView,
    MiningListView,
)

app_name = "admin"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    # User URLs
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<uuid:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    # Investment URLs
    path("investments/", InvestmentListView.as_view(), name="investment-list"),
    path(
        "investments/<uuid:pk>/",
        InvestmentDetailView.as_view(),
        name="investment-detail",
    ),
    path(
        "investments/create/", InvestmentCreateView.as_view(), name="investment-create"
    ),
    path(
        "investments/<uuid:pk>/update/",
        InvestmentUpdateView.as_view(),
        name="investment-update",
    ),
    path(
        "investments/<uuid:pk>/delete/",
        InvestmentDeleteView.as_view(),
        name="investment-delete",
    ),
    # Wallet URLs
    path("wallets/", WalletListView.as_view(), name="wallet-list"),
    path("wallets/<uuid:pk>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("wallets/create/", WalletCreateView.as_view(), name="wallet-create"),
    path("wallets/<uuid:pk>/update/", WalletUpdateView.as_view(), name="wallet-update"),
    path("wallets/<uuid:pk>/delete/", WalletDeleteView.as_view(), name="wallet-delete"),
    # Transaction URLs
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/<uuid:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path(
        "transactions/<uuid:pk>/action/",
        TransactionActionView.as_view(),
        name="transaction-action",
    ),
    path(
        "transactions/<uuid:pk>/delete/",
        TransactionDeleteView.as_view(),
        name="transaction-delete",
    ),
    # Deposit Method URLs
    path(
        "deposit-methods/", DepositMethodListView.as_view(), name="deposit-method-list"
    ),
    path(
        "deposit-methods/<uuid:pk>/",
        DepositMethodDetailView.as_view(),
        name="deposit-method-detail",
    ),
    path(
        "deposit-methods/create/",
        DepositMethodCreateView.as_view(),
        name="deposit-method-create",
    ),
    path(
        "deposit-methods/<uuid:pk>/update/",
        DepositMethodUpdateView.as_view(),
        name="deposit-method-update",
    ),
    path(
        "deposit-methods/<uuid:pk>/delete/",
        DepositMethodDeleteView.as_view(),
        name="deposit-method-delete",
    ),
    path("plans/", PlanListView.as_view(), name="plan-list"),
    path("plans/<uuid:pk>/", PlanDetailView.as_view(), name="plan-detail"),
    path("plans/create/", PlanCreateView.as_view(), name="plan-create"),
    path("plans/<uuid:pk>/update/", PlanUpdateView.as_view(), name="plan-update"),
    path("plans/<uuid:pk>/delete/", PlanDeleteView.as_view(), name="plan-delete"),
    path("minings/", MiningListView.as_view(), name="mining-list"),
    path("minings/<uuid:pk>/", MiningDetailView.as_view(), name="mining-detail"),
    path("minings/create/", MiningCreateView.as_view(), name="mining-create"),
    path("minings/<uuid:pk>/update/", MiningUpdateView.as_view(), name="mining-update"),
    path("minings/<uuid:pk>/delete/", MiningDeleteView.as_view(), name="mining-delete"),
    path("login/", LoginView.as_view(), name="login"),
]
