from django.contrib import admin
from django.contrib.admin import widgets
from fields import ShortTextField

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

class StorybaseModelAdmin(admin.ModelAdmin):
    """ Base class for ModelAdmin classes in this project 

    Correctly sets the widget for our text field class in the Django
    Admin.  It seems like this is the only place you can do it, though
    it would be nice to do it with the field definition.

    """
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }

class StorybaseStackedInline(admin.StackedInline):
    formfield_overrides = {
        ShortTextField: {'widget': AdminLongTextInputWidget},
    }
