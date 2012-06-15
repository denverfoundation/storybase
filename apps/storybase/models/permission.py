class PermissionMixin(object):
    """Interface for model-instance permissions"""
    def has_perms(self, user, perms):
        for perm in perms:
            if not self.has_perm(user, perm):
                return False
        else:
            return True

    def has_perm(self, actor, perm):
        func_name = "%s_can_%s" % (actor.__class__.__name__.lower(), perm)
        func = getattr(self, func_name, None)
        if func is not None:
            return func(actor)
        else:
            return False
