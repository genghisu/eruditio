from django.dispatch import Signal

answer_accepted = Signal(providing_args=["instance"])