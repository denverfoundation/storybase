from django.db.models import Q

from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class UserAuthorization(object):

    def user_valid(self, bundle):
        """
        Is the user associated with the request valid?

        A valid user must exist, be authenticated and be active.
        """
        if (not hasattr(bundle.request, 'user') or
            not bundle.request.user.is_authenticated() or
            not bundle.request.user.is_active):
            raise Unauthorized("You are not allowed to access that resource.")
        else:
            return True


class LoggedInAuthorization(Authorization, UserAuthorization):
    """Custom authorization that checks Django authentication"""

    def filter_by_perms(self, object_list, bundle, perms):
        """
        Filter a list of objects to only the items for which a request's user
        has a particular set of permissions.
        """
        # TODO: Use custom queryset methods to do this at the database
        # level instead of iterating through the list and checking the
        # permissions on each item
        filtered = []

        if self.user_valid(bundle):
            for obj in object_list:
                if (hasattr(obj, 'has_perms') and
                        obj.has_perms(bundle.request.user, perms)):
                    filtered.append(obj)

        return filtered

    def obj_has_perms(self, obj, user, perms):
        """
        Use an object's ``has_perms`` method to check whether the request's
        user has particular permissions for the object.

        Returns either ``True`` if the user has the requested permissions for
        the object in question or throw ``Unauthorized`` if they do not.

        Unlike ``has_perms``, this method allows explicitely specify the
        object and user instead of taking them from the bundle.

        This is useful in cases where you want to check permissions against
        some other object, often in nested resources.

        """
        if (hasattr(obj, 'has_perms') and
            obj.has_perms(user, perms)):
            return True

        raise Unauthorized("You are not allowed to access that resource.")

    def has_perms(self, object_list, bundle, perms):
        """
        Use an object's ``has_perms`` method to check whether the request's
        user has particular permissions for the object.

        Returns either ``True`` if the user has the requested permissions for
        the object in question or throw ``Unauthorized`` if they do not.
        """
        if self.user_valid(bundle):
            return self.obj_has_perms(bundle.obj, bundle.request.user, perms)

        raise Unauthorized("You are not allowed to access that resource.")

    def create_detail(self, object_list, bundle):
        """
        Returns either ``True`` if the user is allowed to create the object in
        question or throw ``Unauthorized`` if they are not.

        Returns ``True`` if the user is authenticated and active.
        """
        return self.user_valid(bundle)

    def update_list(self, object_list, bundle):
        """
        Returns a list of all the objects a user is allowed to update.

        Should return an empty list if none are allowed.

        Delegates to each object in the list's ``has_perms`` method to check
        permissions for the request's user.
        """
        return self.filter_by_perms(object_list, bundle, ['change'])

    def update_detail(self, object_list, bundle):
        """
        Returns either ``True`` if the user is allowed to update the object in
        question or throw ``Unauthorized`` if they are not.

        Delegates to the object's ``has_perms`` method to check permissions
        for the request's user.
        """
        return self.has_perms(object_list, bundle, ['change'])

    def delete_list(self, object_list, bundle):
        """
        Returns a list of all the objects a user is allowed to delete.

        Should return an empty list if none are allowed.

        Delegates to each object in the list's ``has_perms`` method to check
        permissions for the request's user.
        """
        return self.filter_by_perms(object_list, bundle, ['delete'])

    def delete_detail(self, object_list, bundle):
        """
        Returns either ``True`` if the user is allowed to delete the object in
        question or throw ``Unauthorized`` if they are not.

        Delegates to the object's ``has_perms`` method to check permissions
        for the request's user.
        """
        return self.has_perms(object_list, bundle, ['change'])


class PublishedOwnerAuthorization(LoggedInAuthorization):
    """Authorization for models with a publication status and owner user"""

    # This can be overridden is subclasses if the owner field is something
    # other than ``owner``, e.g. ``author``
    owner_field = 'owner'

    # TODO: Move these filtering operations to the model/manager/queryset

    def read_list(self, object_list, bundle):
        # All users can see published items
        q = Q(status='published')
        if (hasattr(bundle.request, 'user') and
                bundle.request.user.is_authenticated()):
            if bundle.request.user.is_superuser:
                # If the user is a superuser, don't restrict the list at all
                return object_list
            else:
                # If the user is logged in, show their unpublished stories as
                # well
                q_args = {
                    self.owner_field: bundle.request.user
                }
                q = q | Q(**q_args)

        return object_list.filter(q)

    def update_list(self, object_list, bundle):
        if not (hasattr(bundle.request, 'user') and
                bundle.request.user.is_authenticated()):
            # Unauthenticated users shouldn't be able to update anything
            return []

        if bundle.request.is_superuser:
            # If the user is a superuser, don't restrict the list at all
            return object_list
        else:
            # For authenticated users, restrict the list to objects that
            # the user owns
            filter_args = {
                self.owner_field: bundle.request.user
            }
            return object_list.filter(**filter_args)

    def delete_list(self, object_list, bundle):
        return self.update_list(object_list, bundle)

