from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from django.core.mail import send_mail
from django.template.loader import render_to_string

@receiver(post_save, sender=Booking)
def send_booking_approval_email(sender, instance, created, **kwargs):
    if created and instance.approved:
        # Render the email content from template
        email_content = render_to_string('text/approval_email.txt', {'client_name': instance.client_name})

        # Send the email
        send_mail(
            'Booking Approval',
            email_content,
            'hostelia33@gmail.com',  # Sender's email
            [instance.client_name.user.email],  # List of recipients
            fail_silently=False,
        )

@receiver(post_save, sender=Booking)
def send_booking_decline_email(sender, instance, created, **kwargs):
    if created and instance.declined:
        # Render the email content from template
        email_content = render_to_string('text/decline_email.txt', {'client_name': instance.client_name})

        # Send the email
        send_mail(
            'Booking Disapproval',
            email_content,
            'hostelia33@gmail.com',  # Sender's email
            [instance.client_name.user.email],  # List of recipients
            fail_silently=False,
        )
