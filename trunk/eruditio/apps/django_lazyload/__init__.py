from django.conf import settings

def autodiscover():
    if not settings.SETUP:
        import django_moderation.moderation
        import django_contenthistory.contenthistory
        import django_badges.badges
        import django_userhistory.userhistory
        import django_reputation.reputation
        import django_community_wiki.community_wiki