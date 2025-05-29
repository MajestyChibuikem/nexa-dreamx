from django.urls import path
from .views import (
    DashboardView,
    PlanListView,
    DepositMethodListView,
    DepositCreateView,
    TransactionDetailView,
    WithdrawalCreateView,
    WithdrawalListView,
    InvestmentCreateView,
    InterestListView,
    DepositListView,
    InvestmentListView,
    WithdrawalListView,
    WithdrawalMethodListView,
    ProfileView,
)

app_name = "user"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("plans/", PlanListView.as_view(), name="plan_list"),
    path("plans/<uuid:pk>/invest/", InvestmentCreateView.as_view(), name="invest"),
    path("investments/", InvestmentListView.as_view(), name="investments"),
    path(
        "investment/<uuid:pk>/details",
        TransactionDetailView.as_view(),
        name="investment_details",
    ),
    path("deposit/", DepositMethodListView.as_view(), name="deposit_methods"),
    path("deposit/<uuid:pk>/", DepositCreateView.as_view(), name="deposit_create"),
    path(
        "deposit/<uuid:pk>/details",
        TransactionDetailView.as_view(),
        name="deposit_details",
    ),
    path("withdraw/", WithdrawalMethodListView.as_view(), name="withdrawal_methods"),
    path(
        "withdraw/<uuid:pk>/", WithdrawalCreateView.as_view(), name="withdrawal_create"
    ),
    path(
        "withdraw/<uuid:pk>/details/",
        TransactionDetailView.as_view(),
        name="withdrawal_details",
    ),
    path("transactions/deposit/all", DepositListView.as_view(), name="deposits"),
    path("transactions/withdraw/all", WithdrawalListView.as_view(), name="withdrawals"),
    path("transactions/interest/all", InterestListView.as_view(), name="interests"),
    path("profile", ProfileView.as_view(), name="profile"),
]
