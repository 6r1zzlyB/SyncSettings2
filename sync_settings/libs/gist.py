# -*- coding: utf-8 -*-

import json
import re
import urllib.request
import urllib.error
from functools import wraps

from .logger import logger


class NotFoundError(RuntimeError):
    pass


class UnexpectedError(RuntimeError):
    pass


class NetworkError(RuntimeError):
    pass


class AuthenticationError(RuntimeError):
    pass


class UnprocessableDataError(RuntimeError):
    pass


class Response:
    def __init__(self, status_code, data=None, reason=None):
        self.status_code = status_code
        self.reason = reason
        self._data = data

    def json(self):
        if self._data is None:
            return {}
        return json.loads(self._data.decode('utf-8'))


def auth(func):
    @wraps(func)
    def auth_wrapper(self, *args, **kwargs):
        if self.token is None:
            raise AuthenticationError('GitHub credentials are required')
        return func(self, *args, **kwargs)

    return auth_wrapper


def with_gid(func):
    @wraps(func)
    def with_gid_wrapper(self, *args, **kwargs):
        if not args[0]:
            raise ValueError(f'The given id `{args[0]}` is not valid')
        return func(self, *args, **kwargs)

    return with_gid_wrapper


class Gist:
    def __init__(self, token=None, http_proxy='', https_proxy=''):
        self.token = token
        self.http_proxy = http_proxy
        self.https_proxy = https_proxy

    @staticmethod
    def make_uri(endpoint=''):
        e = '' if not endpoint else f'/{endpoint}'
        return f'https://api.github.com/gists{e}'

    @auth
    def create(self, data):
        if not isinstance(data, dict) or not len(data):
            raise ValueError("Gist can't be created without data")
        return self.__do_request('POST', self.make_uri(), data=data).json()

    @auth
    @with_gid
    def update(self, gid, data):
        if not isinstance(data, dict) or not len(data):
            raise ValueError("Gist can't be updated without data")
        return self.__do_request('PATCH', self.make_uri(gid), data=data).json()

    @auth
    @with_gid
    def delete(self, gid):
        response = self.__do_request('DELETE', self.make_uri(gid))
        return response.status_code == 204

    @with_gid
    def get(self, gid):
        return self.__do_request('GET', self.make_uri(gid)).json()

    @with_gid
    def commits(self, gid):
        return self.__do_request('GET', self.make_uri(f'{gid}/commits')).json()

    def __do_request(self, verb, url, **kwargs):
        headers = self.headers
        data = kwargs.get('data')
        
        # Phase 2.4 Fix: Unicode encoding
        if data is not None:
            if isinstance(data, (dict, list)):
                json_data = json.dumps(data, ensure_ascii=False)
                data_bytes = json_data.encode('utf-8')
            else:
                data_bytes = data.encode('utf-8')
        else:
            data_bytes = None

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=verb.upper())

        # Proxy handling
        proxies = self.proxies
        if proxies:
            proxy_handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)

        try:
            with urllib.request.urlopen(req) as f:
                return Response(f.getcode(), f.read(), f.reason)
        except urllib.error.HTTPError as e:
            # Create a response object from the error
            try:
                error_body = e.read()
            except Exception:
                error_body = None
            response = Response(e.code, error_body, e.reason)
            
            # Map status codes to exceptions based on legacy logic
            if response.status_code == 404:
                raise NotFoundError('The requested gist does not exist, or the token requires permissions')
            if response.status_code in [401, 403]:
                raise AuthenticationError('Credentials invalid or token missing permissions')
            if response.status_code == 422:
                raise UnprocessableDataError('The provided data has errors')
            if response.status_code >= 300:
                logger.warning(response.json())
                try:
                    msg = response.json().get('message', str(e))
                except Exception:
                    msg = str(e)
                raise UnexpectedError(f'Unexpected Error, Reason: {msg}')
            return response
        except urllib.error.URLError as e:
            raise NetworkError(f'Network error. Reason: {str(e.reason)}')
        except Exception as e:
            raise UnexpectedError(f'Unknown error: {str(e)}')

    @property
    def headers(self):
        h = {
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        if self.token:
            if self.token.startswith('ghp_') or self.token.startswith('github_pat_'):
                h['Authorization'] = f'Bearer {self.token}'
            else:
                h['Authorization'] = f'token {self.token}'
        return h

    @property
    def proxies(self):
        def check_proxy_url(url):
            regex = re.compile(
                r'^(?:http)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return url and isinstance(url, str) and re.match(regex, url) is not None
        proxies = dict()
        if check_proxy_url(self.http_proxy):
            proxies['http'] = self.http_proxy
        if check_proxy_url(self.https_proxy):
            proxies['https'] = self.https_proxy
        return proxies
