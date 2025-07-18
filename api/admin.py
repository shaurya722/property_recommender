from django.contrib import admin
from .models import CustomUser, Property, SearchHistory

admin.site.register(CustomUser)
admin.site.register(Property)
admin.site.register(SearchHistory)