from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    username = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Username"),
        error_messages={"unique": "A user with this username already exist."},
    )
    mobile = models.CharField(
        max_length=15,
        verbose_name=_("Mobile"),
        error_messages={"unique": "A user with this mobile number already exist."},
    )
    country = models.CharField(max_length=255)
    address = models.CharField(max_length=255, verbose_name="Address")
    state = models.CharField(max_length=255, verbose_name="State")
    zip_code = models.CharField(max_length=255, verbose_name="Zip Code")
    city = models.CharField(max_length=255, verbose_name="City")
    profile_photo = models.ImageField(
        upload_to="profile_photos/", null=True, blank=True
    )
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="referrals",
    )

    def __str__(self):
        return self.email


class Referral(models.Model):
    referrer = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="made_referrals"
    )
    referred = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="referral_entry"
    )
    created_at = models.DateTimeField(auto_now_add=True)
