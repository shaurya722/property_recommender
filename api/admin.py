from django.contrib import admin
from .models import CustomUser, Property, SearchHistory, PropertyInterest

admin.site.register(CustomUser)
admin.site.register(Property)
admin.site.register(SearchHistory)
admin.site.register(PropertyInterest)