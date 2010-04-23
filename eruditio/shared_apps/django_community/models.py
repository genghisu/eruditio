import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from django_utils.request_helpers import get_ip
from django.core.exceptions import ObjectDoesNotExist

class UserProfileManager(models.Manager):
    """
    Custom manager for managing user profiles.
    
    Provides functionality for retrieving, editing and creating
    user profiles.
    """
    def get_user_profile(self, user):
        """
        Returns an user's profile.  Creates a new empty
        UserProfile with default parameters if no profile
        currently exists for the target user.
        """
        try:
            user_profile = super(UserProfileManager, self).get(user = user)
        except ObjectDoesNotExist:
            user_profile = self.model(display_name = user.username, user = user)
            user_profile.save()
        return user_profile
    
    def edit_profile(self, user, data):
        """
        Modifies a user's UserProfile with the incoming data.
        """
        profile = self.get_user_profile(user)
        profile.display_name = data.get('display_name', profile.display_name)
        profile.about_me = data.get('about_me', profile.about_me)
        profile.location = data.get('location', profile.location)
        profile.website = data.get('website', profile.website)
        profile.birthdate = data.get('birthdate', None)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        profile.save()
        user.save()
        
    def insert_profile_info(self, user):
        from django.db.models.fields.related import RelatedField
        
        profile = self.get_user_profile(user)
        opts = profile.__class__._meta
        fields = opts.fields
        for field in fields:
            if not isinstance(field, RelatedField) and getattr(user, field.name, None) is None:
                setattr(user, field.name, getattr(profile, field.name))
        return user
    
class UserProfile(models.Model):
    ip_address = models.IPAddressField(_('ip'), blank = True, null = True)
    is_anonymous = models.BooleanField(_('anonymous'), default = False)
    
    website = models.URLField(_('website'), max_length = 200,  blank = True)
    birthdate = models.DateField(_('birthday'), blank = True,  null = True)
    location = models.CharField(_('location'), max_length = 200,  blank = True)
    display_name = models.CharField(_('display name'), max_length = 100,  blank = True)
    about_me = models.TextField(_('about'), default = '',  blank = True)
    
    user = models.OneToOneField(User, related_name = 'profile')
    
    objects = UserProfileManager()
    
    def __unicode__(self):
        return self.user.username

class UserOpenIDManager(models.Manager):
    def get_for_openid(self, request, target_openid):
        try:
            user_openid = super(UserOpenIDManager, self).get(openid = target_openid.openid)
            user = user_openid.user
        except ObjectDoesNotExist:
            from django_community.utils import create_user_from_openid
            user = create_user_from_openid(request, target_openid)
        return user
    
class UserOpenID(models.Model):
    openid = models.TextField()
    date_created = CreationDateTimeField()
    user = models.ForeignKey(User, related_name = 'openids')
    
    objects = UserOpenIDManager()

class FavoriteManager(models.Manager):
    def add(self, object, user):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        favorite = self.model(content_type = content_type_object, object_id = object.id, user = user)
        favorite.save()
        return favorite
    
    def remove(self, object, user):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        try:
            favorite = self.model.objects.get(content_type = content_type_object, object_id = object.id, user = user)
            favorite.delete()
        except ObjectDoesNotExist:
            favorite = None
            
    def favorites_for_object(self, object):
        content_type_object = ContentType.objects.get_for_model(object.__class__)
        return self.model.objects.filter(content_type = content_type_object, object_id = object.id)
    
class Favorite(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    
    user = models.ForeignKey(User)
    
    date_created = CreationDateTimeField()
    
    objects = FavoriteManager()