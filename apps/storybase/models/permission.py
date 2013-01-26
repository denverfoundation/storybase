class PermissionMixin(object):
    """Interface for model-instance permissions"""
    def has_perms(self, user, perms):
        for perm in perms:
            if not self.has_perm(user, perm):
                return False
        else:
            return True

    def has_perm(self, actor, perm):
        actor_class_name = actor.__class__.__name__.lower()
        func_name = "%s_can_%s" % (actor_class_name, perm)
        func = getattr(self, func_name, None)
        if func is not None:
            return func(actor)
        else:
            return False
