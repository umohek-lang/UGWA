from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from .models import MemberProfile


@receiver(post_save, sender=User)
def create_member_profile(sender, instance, created, **kwargs):

    if not instance.is_superuser:

        MemberProfile.objects.get_or_create(
            user=instance
        )