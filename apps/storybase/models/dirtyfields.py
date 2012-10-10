"""
Mixin for being able to check which fields have changed on a model since
it was last saved.

Taken from `django-dirtyfields <https://github.com/smn/django-dirtyfields/>`_  
to avoid having a separate dependency.

"""
import datetime

try:
    # Use the native Django functions if Django >= 1.4
    from django.utils import timezone
except ImportError:
    # Otherwise, use the backported version
    from storybase.utils import timezone

# Copyright (c) Praekelt Foundation and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    1.  Redistributions of source code must retain the above copyright notice, 
#        this list of conditions and the following disclaimer.
#
#    2.  Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#    
#    3.  Neither the name of the Praekelt Foundation nor the names of its
#        contributors may be used to endorse or promote products derived from 
#        this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django
from django.db.models.signals import post_save

class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        post_save.connect(reset_state, sender=self.__class__, 
                            dispatch_uid='%s-DirtyFieldsMixin-sweeper' % self.__class__.__name__)
        reset_state(sender=self.__class__, instance=self)

    def _as_dict(self):
        return dict([(f.name, getattr(self, f.name)) for f in self._meta.local_fields if not f.rel])

    @classmethod
    def _value_changed(cls, old, new):
        return old != new
    
    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if self._value_changed(value, new_state[key])])
    
    def is_dirty(self):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk: 
            return True
        return {} != self.get_dirty_fields()


class TzDirtyFieldsMixin(DirtyFieldsMixin):
    """A timezone-aware version of DirtyFieldsMixin"""
    @classmethod
    def _match_aware(cls, old, new):
        tz = timezone.get_default_timezone()
        if timezone.is_naive(old) and timezone.is_aware(new):
            return (old, timezone.make_naive(new, tz))
        elif timezone.is_aware(old) and timezone.is_naive(new):
            return (timezone.make_naive(old, tz), new)
        else:
            return (old, new)

    @classmethod
    def _value_changed(cls, old, new):
        # Special timezone aware handling goes here
        if isinstance(old, datetime.datetime) and isinstance(new, datetime.datetime):
            (old, new) = cls._match_aware(old, new)
        return super(TzDirtyFieldsMixin, cls)._value_changed(old, new)

def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()
