"""
Mixin for being able to check which fields have changed on a model since
it was last saved.

Taken from `django-dirtyfields <https://github.com/smn/django-dirtyfields/>`_  
to avoid having a separate dependency.

"""

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
    
    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])
    
    def is_dirty(self):
        # in order to be dirty we need to have been saved at least once, so we
        # check for a primary key and we need our dirty fields to not be empty
        if not self.pk: 
            return True
        return {} != self.get_dirty_fields()

def reset_state(sender, instance, **kwargs):
    instance._original_state = instance._as_dict()
