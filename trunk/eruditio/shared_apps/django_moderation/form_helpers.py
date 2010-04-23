import django.forms as forms
from django.forms.util import flatatt, ErrorDict, ErrorList, ValidationError
from django.conf import settings

class DivForm(forms.Form):
    """forms.Form with built in rendering as divs"""
    class Media:
        js = ('forms.js', )

    def as_div(self):
        normal_row =  u"<div class='form_row'><div class='form_left'>%(label)s</div> \
                    <div class='form_right'>%(field)s<span class='help_text'>%(help_text)s</span>%(errors)s</div></div>"
        error_row = u"<div class='form_row'>%s</div>"
        row_end = "</div>"
        help_text = u"%s"
        return self._html_output(normal_row,  error_row,  row_end,  help_text,  False)

class StandardTextarea(forms.Textarea):
    def __init__(self,  *args,  **kws):
        html_attrs = kws.get('attrs',  {})
        html_attrs.setdefault('cols',  55)
        html_attrs.setdefault('rows',  3)
        kws['attrs'] = html_attrs
        super(StandardTextarea,  self).__init__(*args,  **kws)