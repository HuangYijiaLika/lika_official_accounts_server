from django.contrib import admin

from .models import Offer, User


admin.site.register(User)
admin.site.register(Offer)
