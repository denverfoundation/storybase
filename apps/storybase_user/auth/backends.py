from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailModelBackend(ModelBackend):
    """
    Authenticates against django.contrib.auth.models.User using the email field.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
