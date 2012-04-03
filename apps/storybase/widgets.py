"""Custom widgets"""
from django.contrib.admin import widgets

class AdminLongTextInputWidget(widgets.AdminTextInputWidget):
    """ Slightly wider AdminTextInputWidget """
    def __init__(self, attrs=None):
        # Set size attribute as longer than default
        # and override class so text input size doesn't get 
        # shortened by CSS
        final_attrs = {'size': 60, 'class': 'vLongTextField'}
        if attrs is not None:
            final_attrs.update(attrs)
        super(AdminLongTextInputWidget, self).__init__(attrs=final_attrs)
