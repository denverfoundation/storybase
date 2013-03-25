import logging
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

logger = logging.getLogger('storybase.js')

class JSErrorHandlerView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(JSErrorHandlerView, self).dispatch(*args, **kwargs)
   
    def post(self, request, *args, **kwargs):
        """Read POST data and log it as an JS error"""
        error_dict = request.POST.dict()

        error_dict['HTTP_USER_AGENT'] = request.META['HTTP_USER_AGENT']

        if (request.user.is_authenticated()):
            error_dict['user'] = "%s" % (request.user.username)

        # Serialize the error dictionary as JSON, to make it easier to
        # parse the logs on the other side
        logger.error("javascript error: %s", error_dict['message'], extra={
            'data': error_dict,    
        })
        return HttpResponse('Error logged')
