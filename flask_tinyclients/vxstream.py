"""
    flask_tinyclients.vxstream
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    VxStream API client

"""
from urllib.parse import urljoin
import requests
from . import RESTAPIClient


class VxAPIClient(RESTAPIClient):
    base_url = None
    apikey = None
    secret = None

    def request(self, *args, **kwargs):
        method, path, *rest = args
        url = '{0}/{1}'.format(self.base_url, path)

        default_params = {'type': 'json', 'environmentId': 1}
        params = kwargs.pop('params', default_params)
        default_params.update(params)
        use_params = kwargs.pop('use_params', True)
        if use_params is False:
            default_params = {}

        defaults = {
            'headers': {
                'Content-type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Flask Tinyclients ({0})'.
                    format(self.__class__.__name__)
            },
            'auth': (self.apikey, self.secret),
            'params': default_params
        }
        defaults.update(kwargs)
        try:
            response = requests.request(method, url, **defaults)
        except requests.exceptions.RequestException as err:
            raise err
        except Exception as e:
            raise e

        # Content-Type is not correctly returned by VxStream API
        # reported upstream
        if response.raise_for_status() is not None:
            return response.raise_for_status()
        accepts = defaults.get('headers', {}).get('Accept', None)
        if accepts == 'application/json':
            return response.json()
        return response.content


class VxStream(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('REST_CLIENT_VX_BASE_URL', None)
        app.config.setdefault('REST_CLIENT_VX_API_KEY', None)
        app.config.setdefault('REST_CLIENT_VX_API_SECRET', None)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['vxstream'] = self

        self.app = app

    @property
    def system(self):
        return VxAPIClient(
            base_url=urljoin(self.app.config['REST_CLIENT_VX_BASE_URL'], 'system'),
            apikey=self.app.config['REST_CLIENT_VX_API_KEY'],
            secret=self.app.config['REST_CLIENT_VX_API_SECRET'])

    @property
    def api(self):
        return VxAPIClient(
            base_url=urljoin(self.app.config['REST_CLIENT_VX_BASE_URL'], 'api'),
            apikey=self.app.config['REST_CLIENT_VX_API_KEY'],
            secret=self.app.config['REST_CLIENT_VX_API_SECRET'])

    def state(self, **kwargs):
        return self.system.get('state', **kwargs)

    def stats(self):
        return self.system.get('stats')

    def submit(self, data, **kwargs):
        return self.api.post('submit', data=data, **kwargs)

    def submiturl(self, data, **kwargs):
        return self.api.post('submiturl', data=data, **kwargs)
