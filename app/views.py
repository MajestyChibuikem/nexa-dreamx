from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from .models import Plan


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
