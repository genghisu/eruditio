from django.dispatch import Signal

edit = Signal(providing_args=["original", "current", "editor"])