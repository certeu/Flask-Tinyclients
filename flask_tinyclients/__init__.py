import requests
import json
from urllib.parse import urljoin

__version__ = '0.4.5'


class RESTAPIClient(object):
    base_url = None

    def __init__(self, *args, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def request(self, *args, **kwargs):
        method, path, *rest = args
        url = urljoin(self.base_url, path)

        defaults = {
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Flask Tinyclients v{0}'.format(__version__),
            }
        }
        defaults.update(kwargs)
        try:
            response = requests.request(method, url, **defaults)
        except requests.exceptions.RequestException as err:
            raise err

        if response.raise_for_status() is not None:
            return response.raise_for_status()

        accepts = defaults.get('headers', {}).get('Accept', None)
        if accepts == 'application/json':
            return response.json()
        return response.content

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        #kwargs['data'] = json.dumps(kwargs['data'])
        return self.request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('DELETE', *args, **kwargs)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, id(self))

