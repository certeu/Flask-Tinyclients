"""
    flask_tinyclients.fireeye
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    FireEye API client

"""
import functools
import json
from urllib.parse import urljoin

import requests
from flask import session

from . import RESTAPIClient


__all__ = ['FireEye']


KEY_HEADERS = 'headers'

HEADER_ACCEPT = 'Accept'
HEADER_X_FE_API_TOKEN = 'X-FeApi-Token'

APPLICATION_JSON = 'application/json'


class UnauthorizedException(Exception):
    pass


class FEAPIClient(RESTAPIClient):

    API_PATH = '/wsapis/v2.0.0'

    DEFAULT_HEADERS = {
        HEADER_ACCEPT: APPLICATION_JSON,
        'User-Agent': 'Flask Tinyclients (FEAPIClient)'
    }

    STATUS_CODE_UNAUTHORIZED = 401

    base_url = None
    username = None
    secret = None

    def _get_headers(self, kwargs):
        headers = self.DEFAULT_HEADERS.copy()

        # Get and remove "headers" from kwargs
        arg_headers = kwargs.pop(KEY_HEADERS, None)
        if arg_headers is not None:
            headers.update(arg_headers)

        return headers

    def _get_url(self, endpoint):
        path = self.API_PATH + endpoint
        return urljoin(self.base_url, path)

    def _request(self, *args, **kwargs):
        method, endpoint, *rest = args
        url = self._get_url(endpoint)

        return_raw = kwargs.pop('raw_response', None)

        request_kwargs = {
            KEY_HEADERS: self._get_headers(kwargs),
        }
        request_kwargs.update(kwargs)

        try:
            response = requests.request(method, url, **request_kwargs)
        except Exception as e:
            raise e

        if return_raw:
            return response

        if response.status_code == self.STATUS_CODE_UNAUTHORIZED:
            raise UnauthorizedException()

        response.raise_for_status()

        accepts = request_kwargs.get(KEY_HEADERS, {}).get(HEADER_ACCEPT, None)
        if accepts == APPLICATION_JSON:
            return response.json()

        return response.content

    def request(self, *args, **kwargs):
        return self._request(*args, **kwargs)


def _require_auth_token(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        fe, *rest = args

        try:
            value = func(*args, **kwargs)
        except UnauthorizedException:
            _headers = kwargs.get(KEY_HEADERS, None)
            if _headers is None:
                _headers = {}
                kwargs[KEY_HEADERS] = _headers

            token = fe.get_auth_token()

            session['FE_API_TOKEN'] = token

            _headers[HEADER_X_FE_API_TOKEN] = token

            value = func(*args, **kwargs)

        return value
    return _wrapper


class FireEye(object):

    ENDPOINT_AUTH_LOGIN = '/auth/login'
    ENDPOINT_CONFIG = '/config'
    ENDPOINT_SUBMISSIONS = '/submissions'
    ENDPOINT_SUBMISSIONS_URL = ENDPOINT_SUBMISSIONS + '/url'
    ENDPOINT_SUBMISSIONS_STATUS = ENDPOINT_SUBMISSIONS + '/status/{0}'
    ENDPOINT_SUBMISSIONS_RESULTS = ENDPOINT_SUBMISSIONS + '/results/{0}'

    api = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.api = FEAPIClient(
                base_url=app.config['REST_CLIENT_FIREEYE_BASE_URL'],
                username=app.config['REST_CLIENT_FIREEYE_USERNAME'],
                secret=app.config['REST_CLIENT_FIREEYE_API_SECRET'])

    def get_auth_token(self):
        auth = (self.api.username, self.api.secret,)
        response = self.api.post(
            self.ENDPOINT_AUTH_LOGIN, raw_response=True, timeout=120, auth=auth)

        if not response.ok:
            raise UnauthorizedException('Failed authenticate with given credentials')

        token = response.headers.get(HEADER_X_FE_API_TOKEN, None)
        if token is None:
            raise UnauthorizedException('No FireEye API token in the response header')

        return token

    @_require_auth_token
    def config(self, **kwargs):
        return self.api.get(self.ENDPOINT_CONFIG, **kwargs)

    @_require_auth_token
    def submissions(self, options, files, **kwargs):
        for (_, value) in files:
            _, file_obj = value
            # If the FireToken is invalid then the file is still consumed.
            # Make sure that the stream position is at the beginning of the file.
            if file_obj.tell() > 0:
                file_obj.seek(0)

        data = {
            'options': json.dumps(options)
        }

        return self.api.post(self.ENDPOINT_SUBMISSIONS, data=data, files=files, **kwargs)

    @_require_auth_token
    def submissions_url(self, options, **kwargs):
        return self.api.post(self.ENDPOINT_SUBMISSIONS_URL, json=options, **kwargs)

    @_require_auth_token
    def submission_status(self, submission_id, **kwargs):
        endpoint = self.ENDPOINT_SUBMISSIONS_STATUS.format(submission_id)
        return self.api.get(endpoint, **kwargs)

    @_require_auth_token
    def submission_results(self, submission_id, **kwargs):
        endpoint = self.ENDPOINT_SUBMISSIONS_RESULTS.format(submission_id)
        return self.api.get(endpoint, **kwargs)
