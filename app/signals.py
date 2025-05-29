from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from users.models import Referral, CustomUser


@receiver(user_signed_up)
def handle_referral(request, user, **kwargs):
    code = request.session.get("referral_code")
    if not code:
        return

    try:
        referrer = CustomUser.objects.get(username=code)
    except CustomUser.DoesNotExist:
        return

    user.referred_by = referrer
    user.save(update_fields=["referred_by"])

    Referral.objects.create(referrer=referrer, referred=user)
