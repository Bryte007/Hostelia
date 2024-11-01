# admin.py

from django.contrib import admin
from .models import UserP, Hostel, Room, Booking

admin.site.register(UserP)
admin.site.register(Hostel)
admin.site.register(Room)
admin.site.register(Booking)
