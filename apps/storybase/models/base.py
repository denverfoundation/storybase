"""Abstract base classes for common Model functionality"""
from datetime import datetime

from django.db import models

class LicensedModel(models.Model):
    """Abstract base class for models with a license"""
    # Class "constants"
    # For now, we don't set a default value on the field so we
    # can differentiate between the state where the user has
    # selected the license and when they haven't.  If we did set a
    # default, this would be it
    DEFAULT_LICENSE = 'CC BY-NC-SA'

    LICENSES = (
       ('CC BY-NC-SA', u'Attribution-NonCommercial-ShareAlike Creative Commons'),
       ('CC BY-NC', u'Attribution-NonCommercial Creative Commons'),
       ('CC BY-NC-ND', u'Attribution-NonCommercial-NoDerivs Creative Commons'),
       ('CC BY', u'Attribution Creative Commons'),
       ('CC BY-SA', u'Attribution-ShareAlike Creative Commons'),
       ('CC BY-ND', u'Attribution-NoDerivs Creative Commons'),
       ('none', u'None (All rights reserved)')
    )

    # Fields
    license = models.CharField(max_length=25, choices=LICENSES,
                               blank=True)

    class Meta:
        """Model metadata options"""
        abstract = True

    def get_license_name(self, code):
        """Convert a license's code to its full name
        
        Arguments:
        code -- String representing the first element of a tuple in LICENSES.
                This is what is stored in the database for a LicensedModel.

        """
        licenses = dict(self.LICENSES)
        return licenses[code]

    def license_name(self):
        """ Convert the license code to a more human-readable version """
        return self.get_license_name(self.license)


class PublishedModel(models.Model):
    """Abstract base class for models with publication information"""
    # Class-level "constants"
    STATUS = (
        (u'pending', u'pending'),
        (u'draft', u'draft'),
        (u'staged', u'staged'),
        (u'published', u'published'),
    )

    DEFAULT_STATUS = u'draft'

    # Fields
    status = models.CharField(max_length=10, choices=STATUS,
                              default=DEFAULT_STATUS)
    published = models.DateTimeField(blank=True, null=True)

    class Meta:
        """Model metadata options"""
        abstract = True

    @property
    def never_published(self):
        """Check if the model has ever been published"""
        return self.published == None


# Signal handlers
def set_date_on_published(sender, instance, **kwargs):
    """Set the published date of a story on status change
    
    For models inheriting from PublishedModel. Should be connected
    to the pre_save signal.

    """
   
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field won't have changed.
        # Just check status.
        if instance.status == 'published':
            instance.published = datetime.now()
    else:
        if (instance.status == 'published' and 
            old_instance.status != 'published'):
            instance.published = datetime.now()


class TimestampedModel(models.Model):
    """ Abstract base class that provides created and last edited fields """
    created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata options"""
        abstract = True


class WeightedModel(models.Model):
    """
    Abstract base class for models with a field that defines the relative
    "weight" of instances when sorting
    """

    # Fields
    weight = models.IntegerField(default=0)

    class Meta:
        """Model metadata options"""
        abstract = True

    def get_weight(self):
        """
        Calculate a new value for the weight fieldi
        
        This should be implemented in subclasses that inherit
        from weighted model.
        """
        raise NotImplementedError
