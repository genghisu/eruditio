import django_userhistory.models as models
from django.contrib import admin

try:
    admin.site.register(models.UserAction)
    admin.site.register(models.UserHistory)
    admin.site.register(models.UserTrackedContent)
except Exception, e:
    pass