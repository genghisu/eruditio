import django_moderation.models as models
from django.contrib import admin

try:
    admin.site.register(models.ContentFlagSet)
    admin.site.register(models.ContentFlag)
    admin.site.register(models.ContentFlagSetMember)
    admin.site.register(models.Reason)
    admin.site.register(models.ContentFlagInstance)
    admin.site.register(models.ContentFlagVote)
    admin.site.register(models.ContentApprovalVote)
    admin.site.register(models.ModeratedContent)
    admin.site.register(models.CommunityWikiContent)
except Exception:
    pass
