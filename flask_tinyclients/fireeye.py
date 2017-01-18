"""
    flask_tinyclients.fireeye
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    FireEye API client

"""
import json
import functools
from urllib.parse import urljoin

from flask import session, _app_ctx_stack, g
import requests
from . import RESTAPIClient

__all__ = ['FireEye']


class FEAPIClient(RESTAPIClient):
    base_url = None
    username = None
    secret = None

    def request(self, *args, **kwargs):
        method, path, *rest = args
        path = '/wsapis/v1.1.0' + path
        url = urljoin(self.base_url, path)
        return_raw = kwargs.pop('raw_response', None)

        defaults = {
            'headers': {
                'Content-type': 'application/json',
                'Accept': 'application/json application/xml',
                'User-Agent': 'Flask Tinyclients ({0})'.
                format(self.__class__.__name__)
            }
        }
        defaults.update(kwargs)
        #: todo: if 401 get a new token by making a auth_request
        try:
            response = requests.request(method, url, **defaults)
        except requests.exceptions.RequestException as err:
            raise err
        except Exception as e:
            raise e

        if response.status_code == 401:
            token = self.get_auth_token(self.username, self.secret)
            headers = {
                'X-FeApi-Token': token
            }
            session['FE_API_TOKEN'] = token
            req = functools.partial(self.request, *args, headers=headers)
            return req.__call__()


        if response.raise_for_status() is not None:
            return response.raise_for_status()
        accepts = defaults.get('headers', {}).get('Accept', None)
        if return_raw:
            return response
        if accepts == 'application/json':
            return response.json()
        return response.content

    def get_auth_token(self, username, password):
        headers = {
            'User-Agent': 'Flask Tinyclients ({0})'.
            format(self.__class__.__name__)
        }
        response = self.post('/auth/login',
                             headers=headers,
                             raw_response=True,
                             timeout=120,
                             auth=(username, password))
        return response.headers.get('X-FeApi-Token', None)


class FireEye(object):

    api = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.api = FEAPIClient(
                base_url=app.config['REST_CLIENT_FIREEYE_BASE_URL'],
                username=app.config['REST_CLIENT_FIREEYE_USERNAME'],
                secret=app.config['REST_CLIENT_FIREEYE_API_SECRET'])

    def submit(self, data, **kwargs):
        return self.api.post('/submissions',
                             data=dict(options=json.dumps(data)),
                             **kwargs)

    def submiturl(self, data, **kwargs):
        return self.api.post('/submissions/url', data=data, **kwargs)
