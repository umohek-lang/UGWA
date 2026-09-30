from .models import AssociationProfile


def get_association():

    return AssociationProfile.objects.filter(
        is_active=True
    ).first()