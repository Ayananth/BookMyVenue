from django.contrib import admin
from .models import Venue, VenueSchedule, VenueScheduleGroup

admin.site.register(Venue)
admin.site.register(VenueSchedule)
admin.site.register(VenueScheduleGroup)

