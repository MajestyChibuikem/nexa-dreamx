# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Referral
from django.conf import settings


@receiver(post_save, sender=Referral)
def notify_referrer(sender, instance, created, **kwargs):
    if not created:
        return
    ref = instance.referrer
    new_user = instance.referred
    send_mail(
        subject="🌟 Your Referral Bonus is Activated! 🌟",
        message=(
            f"Hi {ref.first_name},\n\n"
            f"🎉 Big news! {new_user.first_name} just joined Nexa Wealth using your referral link.\n\n"
            "We want to personally thank you for spreading the word about our platform. "
            "Because of awesome members like you, our community grows stronger every day!\n\n"
            "✨ Here's what happens next:\n"
            "- Your referral bonus has been credited to your account\n"
            f"- You're now one step closer to our exclusive VIP referral tiers (Total referrals: {ref.made_referrals.count()})\n"
            f"- Together, you and {new_user.first_name} can watch your investments grow\n\n"
            "Want to earn even more rewards? Keep sharing your unique link:\n"
            f"{settings.APP_URL}/accounts/signup/?ref={ref.username}\n\n"
            "Thank you for being a vital part of our success story!\n\n"
            "Warm regards,\n"
            "Alexandra Peters\n"
            "Community Growth Manager\n"
            "Nexa Wealth\n\n"
            f"P.S. Every referral makes a difference! 🌱 We're here to support your financial journey - "
            f"reach out anytime at {getattr(settings, 'SUPPORT_EMAIL', 'help.nexawealth@gmail.comcom')}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[ref.email],
    )
