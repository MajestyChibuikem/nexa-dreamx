from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("app.urls", namespace="public")),
    path("admin/", include("_admin.urls", namespace="admin")),
    path("dashboard/", include("_user.urls", namespace="user")),
    path("accounts/", include("allauth.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "app.views.custom_error_404"
handler500 = "app.views.custom_error_500"
