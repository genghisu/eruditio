from django.db import models

class ConfigManager(models.Manager):
    pass

class ConfigOption(models.Model):
    name = models.CharField(max_length = 75)
    app = models.CharField(max_length = 75)
    help_text = models.TextField(default = '')
    default = models.TextField(default = '')
    available_options = models.TextField(default = '')
    required = models.BooleanField(default = True)
    
    objects = ConfigManager()

    def __unicode__(self):
        return "%s --> %s" % (self.app, self.name)
    
class DefinedConfigOption(models.Model):
    option = models.ForeignKey(ConfigOption)
    value = models.TextField(default = '')
    
    def __unicode__(self):
        return "%s --> %s" % (self.option.app, self.option.name)
    
class ConfigFixture(models.Model):
    help_text = models.TextField(default = '')
    app_label = models.CharField(max_length = 75)
    module_name = models.CharField(max_length = 75)
    
    def full_name(self):
        return "%s_%s" % (self.app_label, self.module_name)
    
    def __unicode__(self):
        return "%s --> %s" % (self.app_label, self.module_name)