from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from venues.models import VenueCategory
from venues.services.category_cache_service import CategoryCacheService


@receiver(post_save, sender=VenueCategory)
@receiver(post_delete, sender=VenueCategory)
def invalidate_venue_category_cache(sender, **kwargs):
    CategoryCacheService.invalidate()
