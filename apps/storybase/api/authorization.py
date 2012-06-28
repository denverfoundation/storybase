from tastypie.authorization import Authorization

class LoggedInAuthorization(Authorization):
    """Custom authorization that checks Django authentication"""
    def is_authorized(self, request, object=None):
        # GET-style methods are always allowed.
        if request.method in ('GET', 'OPTIONS', 'HEAD'):
            return True

        # Users must be logged-in and active in order to use
        # non-GET-style methods
        if (not hasattr(request, 'user') or
            not request.user.is_authenticated or 
            not request.user.is_active):
            return False

        # Logged in users can create new objects
        if request.method in ('POST') and object is None:
            return True

        permission_map = {
            'POST': ['add'],
            'PUT': ['change'],
            'DELETE': ['delete'],
            'PATCH': ['add', 'change', 'delete'],
        }
        permission_codes = permission_map[request.method]

        if hasattr(object, 'has_perms'):
            # If the object supports row-level permissions,
            return object.has_perms(request.user, permission_codes)

        # Fall-back to failure
        return False 
