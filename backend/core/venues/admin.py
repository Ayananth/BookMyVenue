from django.contrib import admin
from .models import City, District, Venue, VenueSchedule, VenueScheduleGroup

admin.site.register(District)
admin.site.register(City)

admin.site.register(Venue)
admin.site.register(VenueSchedule)
admin.site.register(VenueScheduleGroup)

