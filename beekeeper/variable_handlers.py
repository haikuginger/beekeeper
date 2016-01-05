from .parsers import decode, encode
from .variables import Variables
from .utils import request

class Request:

    def __init__(self, action, variables):
        self.data = None
        self.action = action
        self.variables = variables

    def render_variables(self, **kwargs):
        return self.variables.render(self.action)
        
    def send(self):
        return Response(self.action, request(**self.render_variables()))

class Response:

    def __init__(self, action, response):
        self.action = action
        self.headers = dict(response.headers)
        self.data = response.read().decode(self.encoding())
        self.response_code = response.status
        self.response_message = response.reason

    def mimetype(self):
        if ';' in self.headers['Content-Type']:
            return self.headers['Content-Type'].split(';')[0]
        return self.headers.get('Content-Type', self.format())

    def format(self):
        return self.action.format(direction='returns')

    def encoding(self):
        if 'charset=' in self.headers['Content-Type']:
            return self.headers['Content-Type'].split('charset=')[1].split(';')[0]
        return 'utf-8'

    def cookies(self):
        if self.headers.get('Set-Cookie', False):
            return self.headers.get('Set-Cookie').split('; ')
        return []

    def read(self):
        return decode(self.data, self.mimetype())
