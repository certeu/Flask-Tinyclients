"""
    flask_tinyclients.nessus
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Nessus API client

"""
from urllib.parse import urljoin
import requests
from . import RESTAPIClient

__all__ = ['Nessus']


class NessusAPIClient(RESTAPIClient):
    base_url = None
    accesskey = None
    secretkey = None

    def request(self, *args, **kwargs):
        method, path, *rest = args
        url = urljoin(self.base_url, path)

        defaults = {
            'headers': {
                'Content-type': 'application/json',
                'Accept': 'application/json',
                'X-ApiKeys': 'accessKey={0}; secretKey={1}'.
                    format(self.accesskey, self.secretkey),
                'User-Agent': 'Flask Tinyclients ({0})'.
                    format(self.__class__.__name__)
            },
        }
        defaults.update(kwargs)
        try:
            response = requests.request(method, url, **defaults)
        except requests.exceptions.RequestException as err:
            raise err
        except Exception as e:
            raise e

        if response.raise_for_status() is not None:
            return response.raise_for_status()
        accepts = defaults.get('headers', {}).get('Accept', None)
        if accepts == 'application/json':
            return response.json()
        return response.content


class Nessus(object):

    api = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.api = NessusAPIClient(
                    base_url=app.config['REST_CLIENT_NESSUS_BASE_URL'],
                    accesskey=app.config['REST_CLIENT_NESSUS_API_KEY'],
                    secretkey=app.config['REST_CLIENT_NESSUS_API_SECRET'])

    def submit(self, data, **kwargs):
        return self.api.post('scans', data=data, **kwargs)

    def submiturl(self, data, **kwargs):
        return self.api.post('scans', data=data, **kwargs)
