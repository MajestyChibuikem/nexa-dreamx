from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
import os


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"  # Replace with your actual app name

    def ready(self):
        """Connects the post_migrate signal to create an admin user after migrations."""
        post_migrate.connect(create_default_admin, sender=self)


def create_default_admin(sender, **kwargs):
    """Creates a default admin account if one doesn't exist after migrations."""
    from django.db.utils import OperationalError, ProgrammingError

    User = get_user_model()

    try:
        admin_email = os.getenv("SUPERUSER_EMAIL")
        admin_username = os.getenv("SUPERUSER_USERNAME")
        admin_password = os.getenv("SUPERUSER_PASSWORD")

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                email=admin_email,
                username=admin_username,
                password=admin_password,
            )
            print(f"✅ Admin account created: {admin_email}")
        else:
            print("✅ Admin account already exists. Skipping creation.")

    except (OperationalError, ProgrammingError):
        print("⚠️ Database not ready yet. Skipping admin creation.")
