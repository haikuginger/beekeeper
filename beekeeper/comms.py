from .variable_handlers import render
from .data_handlers import decode
import urllib.request

def download_as_json(url):
    """
    Download the data at the URL and load it as JSON
    """
    return json.loads(request(url=url).read().decode('utf-8'))

def request(*args, **kwargs):
    """
    Make a request with the received arguments and return an
    HTTPResponse object
    """
    req = urllib.request.Request(*args, **kwargs)
    return urllib.request.urlopen(req)

class Request:

    def __init__(self, action, variables, verbose=False):
        self.action = action
        self.variables = variables
        self.verbose = verbose
        self.output = {}
        self.output['data'] = None
        self.output['headers'] = {}
        self.output['url'] = self.action.endpoint.url().format(**variables.replacements()) + '?'
        self.render_variables()

    def render_variables(self):
        for var_type in self.variables.types():
            for var in render(var_type, **self.variables.vals(var_type)):
                self.set(var)

    def print_out(self):
        print('URL: {}'.format(self.output['url']))
        print('Headers:')
        if self.output['headers']:
            for x, y in self.output['headers'].items():
                print('{}: {}'.format(x, y))
        else:
            print('None')
        
        print('Data:\n{}'.format(str(self.output['data'])))

        
    def send(self):
        if self.verbose:
            self.print_out()
            return Response(self.action, request(**self.output))
        else:
            return Response(self.action, request(**self.output)).read()

    def set(self, variable):
        method_map = {
            'url_param': self.set_url_param,
            'header': self.set_url_param,
            'data': self.set_data
        }
        assert variable['type'] in method_map
        method_map[variable['type']](variable)

    def set_header(self, header):
        self.output['headers'][header['name']] = header['value']

    def set_data(self, data):
        self.output['data'] = data['data']
        self.output['headers']['Content-Type'] = data['mimetype']

    def set_url_param(self, param):
        self.output['url'] += '{}={}&'.format(param['name'], param['value'])

class Response:

    def __init__(self, action, response):
        self.action = action
        self.headers = dict(response.headers)
        self.data = response.read().decode(self.encoding())
        self.code = response.status
        self.message = response.reason

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