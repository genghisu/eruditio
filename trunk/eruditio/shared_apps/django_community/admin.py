import django_community.models
from django.contrib import admin

admin.site.register(django_community.models.UserProfile)
admin.site.register(django_community.models.UserOpenID)
