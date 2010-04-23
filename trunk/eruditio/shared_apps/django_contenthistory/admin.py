import django_contenthistory.models as models
from django.contrib import admin

class InlineModelField(admin.TabularInline):
    model = models.ModelField
    
class TrackedContentAdmin(admin.ModelAdmin):
    inlines = [InlineModelField,]

try:
    admin.site.register(models.TrackedContent, TrackedContentAdmin)
    admin.site.register(models.ModelField)
    admin.site.register(models.ModelHistory)
except Exception, e:
    pass