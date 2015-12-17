"""Custom widgets"""
from django import forms
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


class Select2Select(forms.Select):
    """
    Select widget enabled with the Select2 JavaScript Library

    This widget simply adds a CSS class to identify the select entity to
    client-side JavaScript.

    The widget must be used in a context that loads the JavaScript for
    the the additional functionality to be loaded.

    """
    def __init__(self, attrs=None):
        super(Select2Select, self).__init__(attrs)
        css_class = self.attrs.get('class', None)
        css_class = css_class + ' select2-enable' if css_class else 'select2-enable'
        self.attrs['class'] = css_class
