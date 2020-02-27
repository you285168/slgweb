from functools import partial
from django.utils.deprecation import MiddlewareMixin
from werkzeug.local import LocalStack, LocalProxy


def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        return top
    return getattr(top, name)


_request_ctx_stack = LocalStack()
global_request = LocalProxy(partial(_lookup_req_object, 'request'))
global_user = LocalProxy(partial(_lookup_req_object, 'user'))
g = LocalProxy(partial(_lookup_req_object, 'g'))


class _RequestGlobals(object):
    pass


class _RequestContext(object):

    def __init__(self, request):
        self.request = request
        self.g = _RequestGlobals()
        self.user = request.user
        self.g.body = request.body
        self.g.headers = request.headers


class GlobalRequestContext(MiddlewareMixin):

    # def process_request(self, request):
    #     _request_ctx_stack.push(_RequestContext(request))

    def process_view(self, request, callback, callback_args, callback_kwargs):
        _request_ctx_stack.push(_RequestContext(request))
        return None

    def process_response(self, request, response):
        _request_ctx_stack.pop()
        return response

    def process_exception(self, request, exception):
        _request_ctx_stack.pop()