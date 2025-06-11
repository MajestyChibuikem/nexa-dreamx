from django.urls import path
from . import views
from .views import WithdrawalView, WithdrawalListView

app_name = "public"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("plan/", views.PlanListView.as_view(), name="plan"),
    path('withdraw/', WithdrawalView.as_view(), name='withdraw'),
    path('withdrawals/', WithdrawalListView.as_view(), name='withdrawals'),
]
