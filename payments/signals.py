from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Payment
from .services import update_invoice_from_payments


@receiver(post_save, sender=Payment)
def payment_saved(sender, instance, **kwargs):

    update_invoice_from_payments(
        instance.invoice
    )


@receiver(post_delete, sender=Payment)
def payment_deleted(sender, instance, **kwargs):

    update_invoice_from_payments(
        instance.invoice
    )