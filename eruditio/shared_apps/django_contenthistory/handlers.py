try:
    import json
except:
    import simplejson as json

from django_contenthistory.models import TrackedContent, ModelField, ModelHistory
import django_contenthistory.signals as signals
from django_contenthistory.utils import generate_diff

class BaseHistoryHandler(object):
    """
    Default handler for creating ModelHistory objects.
    """
    def __init__(self, content_type_object):
        self.content_type_object = content_type_object
        self.model = content_type_object.model_class()
        self.tracked_content_object = TrackedContent.objects.get(content_type = content_type_object)
        self.fields = ModelField.objects.filter(content = self.tracked_content_object)
        signals.edit.connect(self._signal_callback, sender=self.model, weak = False)
    
    def _signal_callback(self, **kwargs):
        original = kwargs['original']
        current = kwargs['current']
        editor = kwargs['editor']
        self.save_history(original, current, editor)
    
    def save_history(self, original, current, editor):
        """
        Saves a ModelHistory object if the target object has been modified.
        """
        created, object_id, data, modified = self.get_data(original, current)
        if modified:
            object_history = ModelHistory.objects.add_history(content_type = self.content_type_object, 
                                                              object_id = object_id,
                                                              data = data,
                                                              editor = editor, 
                                                              created = created)
        
    def get_data(self, original, current):
        """
        Compares the data between the original object and the modified object. Generates
        diffs as necessary and checks to see if any modifications have occurred.
        """
        object_id = current.id
        created = not bool(original)
        modified = not bool(original)
        data = {}
        for field in self.fields:
            if field.mode == ModelField.M2M:
                original_field = ":::".join(sorted(getattr(original, field.name, [])))
                current_field = ":::".join(sorted(getattr(current, field.name, [])))
            elif field.mode == ModelField.TEXT:
                original_field = getattr(original, field.name, None)
                current_field = getattr(current, field.name, None)
            elif field.mode == ModelField.OWNER:
                original_field = getattr(original, field.name, None).username
                current_filed = getattr(current, field.name, None).username
            if not created and original_field and current_field:
                if not original_field == current_field:
                    if field.mode == ModelField.OWNER:
                        data[field.name] = {'old_owner':original_field, 'new_owner':current_field}
                    elif field.mode == ModelField.M2M:
                        data[field.name] = generate_diff(original_field, current_field, True)
                    else:
                        data[field.name] = generate_diff(original_field, current_field)
                    modified = True
                else:
                    data[field.name] = None
        return created, object_id, json.dumps(data), modified