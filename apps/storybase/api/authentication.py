from tastypie.authentication import Authentication


class LoggedInAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        return request.user.is_authenticated()

