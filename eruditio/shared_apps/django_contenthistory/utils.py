import difflib
try:
    import json
except:
    import simplejson as json

from django.template import Variable, VariableDoesNotExist
from django.template.context import Context

from django_contenthistory.models import TrackedContent, ModelHistory, ModelField

def generate_diff(original,  final, m2m = False):
    """
    Given two strings, generate a human readable diff between the two.
    """
    differ = difflib.SequenceMatcher(None,  original,  final)
    if m2m:
        result = show_m2m_diff(differ)
    else:
        result = show_diff(differ)
    return result

def show_diff(seqm):
    """Unify operations between two compared strings seqm is a difflib.SequenceMatcher instance whose a & b are strings"""
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append(seqm.a[a0:a1])
        elif opcode == 'insert':
            output.append("<span class='revision_add'>" + seqm.b[b0:b1] + "</span>")
        elif opcode == 'delete':
            output.append("<span class='revision_delete'>" + seqm.a[a0:a1] + "</span>")
        elif opcode == 'replace':
            output.append("<span class='revision_delete'>" + seqm.a[a0:a1] + "</span>")
            output.append("<span class='revision_add'>" + seqm.b[b0:b1] + "</span>")
        else:
            raise RuntimeError, "unexpected opcode"
    return ''.join(output)

def show_m2m_diff(seqm):
    """
    Unify operations between two compared strings seqm is a difflib.SequenceMatcher instance whose a & b are strings.
    Special cased for M2M diffs, useful for comparing changes to tags.
    """
    output= []
    for opcode, a0, a1, b0, b1 in seqm.get_opcodes():
        if opcode == 'equal':
            output.append("".join(["<span class='revision_uc'>" + x + "</span>" for x in seqm.a[a0:a1].split(":::") if x.strip()]))
        elif opcode == 'insert':
            output.append("".join(["<span class='revision_add'>" + x + "</span>" for x in seqm.b[b0:b1].split(":::") if x.strip()]))
        elif opcode == 'delete':
            output.append("".join(["<span class='revision_delete'>" + x + "</span>" for x in seqm.a[a0:a1].split(":::") if x.strip()]))
        elif opcode == 'replace':
            output.append("<span class='revision_delete'>" + seqm.a[a0:a1] + "</span>")
            output.append("<span class='revision_add'>" + seqm.b[b0:b1] + "</span>")
        else:
            raise RuntimeError, "unexpected opcode"
    return ' '.join(output)

def associate_revision_fields(edit):
    """
    Associate the relevant fields of the target object (fields that have changed)
    with a ModelHistory object.  Used for the history view.
    """
    tracked_content_object = TrackedContent.objects.get(content_type = edit.content_type)
    fields = ModelField.objects.filter(content = tracked_content_object)
    
    revision_data = json.loads(edit.data)
    revision_fields = []
    for field in fields:
        if revision_data.get(field.name, None):
            current_field = {}
            current_field['name'] = field.name
            current_field['mode'] = field.mode
            current_field['content'] = revision_data.get(field.name)
            revision_fields.append(current_field)
    edit.fields = revision_fields
    return edit

def resolve_variable(variable,  context,  default = None):
    if not variable[0] == variable[-1] == '"':
        try:
            resolved_variable = Variable(variable).resolve(context)
        except VariableDoesNotExist:
            if default == None:
                resolved_variable = None
            else:
                resolved_variable = default
    else:
        resolved_variable = str(variable[1:-1])
    return resolved_variable