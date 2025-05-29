from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_user_email(user, subject, template_name, context=None):
    """
    Sends an email to the specified user.

    :param user: User instance to whom the email will be sent.
    :param subject: Subject line of the email.
    :param template_name: Name of the email template (without extension).
    :param context: Context dictionary for rendering the email template.
    """
    context = context or {}
    context.update({"user": user})

    # Render email content
    message = render_to_string(f"emails/{template_name}.html", context)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
