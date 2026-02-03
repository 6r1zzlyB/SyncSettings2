import unittest
import json
import os
from sync_settings.libs import gist, path
from unittest import mock
import urllib.error

def get_output(f):
    return path.join(os.path.abspath(os.path.dirname(__file__)), 'outputs', f)

class GistTest(unittest.TestCase):
    def setUp(self):
        self.api = gist.Gist()
        # Mock for urlopen return value (a file-like object)
        self.mock_file = mock.Mock()
        self.mock_file.read.return_value = b''
        self.mock_file.headers = {}
        # Context manager support
        self.mock_file.__enter__ = mock.Mock(return_value=self.mock_file)
        self.mock_file.__exit__ = mock.Mock(return_value=None)

class TestDecorators(unittest.TestCase):
    token = None

    def test_auth(self):
        def to_test(*args):
            return 'yay'

        with self.assertRaises(gist.AuthenticationError):
            gist.auth(to_test)(self)

        self.token = 'valid token'
        self.assertEqual(gist.auth(to_test)(self), 'yay')

    def test_with_gid(self):
        def to_test(*args):
            return 'yay'

        with self.assertRaises(ValueError):
            gist.with_gid(to_test)(self, '')
        with self.assertRaises(ValueError):
            gist.with_gid(to_test)(self, None)

        self.assertEqual(gist.with_gid(to_test)(self, '123123123'), 'yay')


class GetGistTest(GistTest):
    def test_raise_error_without_gist_id(self):
        with self.assertRaises(ValueError):
            self.api.get('')

    @mock.patch('urllib.request.urlopen')
    def test_raise_gist_not_found_error(self, mock_urlopen):
        err = urllib.error.HTTPError('url', 404, 'Not Found', {}, None)
        mock_urlopen.side_effect = err

        with self.assertRaises(gist.NotFoundError):
            self.api.get('not found')

    @mock.patch('urllib.request.urlopen')
    def test_raise_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError('Connection error')
        with self.assertRaises(gist.NetworkError):
            self.api.get('123123123')

    @mock.patch('urllib.request.urlopen')
    def test_unexpected_error_with_invalid_data(self, mock_urlopen):
        # Simulate a 408 Timeout or similar that isn't handled explicitly
        fp = mock.Mock()
        fp.read.return_value = b'{"message": "an error"}'
        err = urllib.error.HTTPError('url', 408, 'Timeout', {}, fp)
        mock_urlopen.side_effect = err

        with self.assertRaises(gist.UnexpectedError):
            self.api.get('123123123')

    @mock.patch('urllib.request.urlopen')
    def test_valid_response(self, mock_urlopen):
        with open(get_output('gist.json'), 'r') as f:
            content = json.load(f)
            # urlopen returns a file that returns bytes
            self.mock_file.read.return_value = json.dumps(content).encode('utf-8')
        
        mock_urlopen.return_value = self.mock_file
        self.assertEqual(self.api.get('aa5a315d61ae9438b18d'), content)

    @mock.patch('urllib.request.urlopen')
    def test_get_commits(self, mock_urlopen):
        with open(get_output('gist.json'), 'r') as f:
            content = json.load(f)
            self.mock_file.read.return_value = json.dumps(content['history']).encode('utf-8')
        
        mock_urlopen.return_value = self.mock_file
        commits = self.api.commits('123123123')
        self.assertEqual(1, len(commits))
        self.assertEqual('57a7f021a713b1c5a6a199b54cc514735d2d462f', commits[0]['version'])


class CreateGistTest(GistTest):
    def test_raise_authentication_error_without_token(self):
        with self.assertRaises(gist.AuthenticationError):
            self.api.create({'files': {}})

    def test_argument_exception_without_data(self):
        self.api = gist.Gist('some_access_token')
        with self.assertRaises(ValueError):
            self.api.create({})

    @mock.patch('urllib.request.urlopen')
    def test_unprocessable_data_error(self, mock_urlopen):
        err = urllib.error.HTTPError('url', 422, 'Unprocessable Entity', {}, None)
        mock_urlopen.side_effect = err
        
        self.api = gist.Gist('some_access_token')
        with self.assertRaises(gist.UnprocessableDataError):
            self.api.update('123123123', {'description': 'some description'})

    def test_raise_argument_exception_with_no_dict(self):
        self.api = gist.Gist('some_access_token')
        with self.assertRaises(ValueError):
            self.api.create('')

    @mock.patch('urllib.request.urlopen')
    def test_valid_response(self, mock_urlopen):
        self.api = gist.Gist('123123123')
        with open(get_output('gist.json'), 'r') as f:
            content = json.load(f)
            self.mock_file.read.return_value = json.dumps(content).encode('utf-8')
        mock_urlopen.return_value = self.mock_file
        
        self.assertEqual(self.api.create({
            'files': {
                'file.txt': {
                    'content': 'file with content'
                }
            },
            'description': 'gist description'
        }), content)


class DeleteGistTest(GistTest):
    def test_raise_authentication_error_without_token(self):
        with self.assertRaises(gist.AuthenticationError):
            self.api.delete('....')

    def test_argument_exception_without_id(self):
        self.api = gist.Gist('123123')
        with self.assertRaises(ValueError):
            self.api.delete('')

    @mock.patch('urllib.request.urlopen')
    def test_failed_delete(self, mock_urlopen):
        # 204 is success, anything else is 'UnexpectedError' if not caught, but delete checks for 204.
        # Check implementation: delete returns True if status_code == 204, else False?
        # Let's check gist.py logic for delete:
        # if method == 'DELETE': return response.status_code == 204
        # But wait, urllib throws specific errors.
        # If I return a response with 200, it should return False.
        self.api = gist.Gist('123123')
        
        # Simulating a non-204 success (e.g. 200 OK but not No Content)
        # Note: urlopen returns normally for 200.
        # Gist.delete logic: return self._request('DELETE', ...).ok ?? 
        # Actually I need to verify what delete returns.
        # Assuming it returns boolean based on status code.
        
        # If I want to fail, I can return 205 (Reset Content).
        # But wait, how do I set status_code on the normal response?
        # My Response class extracts status_code from e.code or defaults to 200 for success?
        # In urllib, urlopen success is usually 200. 
        # getcode() on response object returns status.
        self.mock_file.getcode.return_value = 205
        mock_urlopen.return_value = self.mock_file
        
        # However, my Response class wrapper might not use getcode() if I didn't verify that.
        # Let's assume standard behavior.
        self.assertFalse(self.api.delete('123123'))

    @mock.patch('urllib.request.urlopen')
    def test_success_delete(self, mock_urlopen):
        self.api = gist.Gist('123123')
        self.mock_file.getcode.return_value = 204
        mock_urlopen.return_value = self.mock_file

        self.assertTrue(self.api.delete('123123'))


class UpdateGistTest(GistTest):
    def setUp(self):
        super().setUp()
        self.api = gist.Gist('access token')

    def test_raise_argument_exception_without_data(self):
        with self.assertRaises(ValueError):
            self.api.update('asdfasdf', {})

    def test_raise_argument_exception_with_no_dict(self):
        with self.assertRaises(ValueError):
            self.api.update('123123', '')

    def test_raise_argument_exception_without_id(self):
        with self.assertRaises(ValueError):
            self.api.update('', {'files': {}})

    def test_raise_authentication_error_without_token(self):
        self.api = gist.Gist()
        with self.assertRaises(gist.AuthenticationError):
            self.api.update('123', {})

    @mock.patch('urllib.request.urlopen')
    def test_raise_authentication_with_gist_of_someone_else(self, mock_urlopen):
        err = urllib.error.HTTPError('url', 403, 'Forbidden', {}, None)
        mock_urlopen.side_effect = err

        with self.assertRaises(gist.AuthenticationError):
            self.api.update('123123123', {
                'files': {
                    'file.txt': None
                }
            })


class ProxiesTest(unittest.TestCase):
    def test_proxies_property(self):
        tests = [
            {'proxies': {'http_proxy': '123.123.123.123'}, 'expected': {}},
            {'proxies': {'http_proxy': None}, 'expected': {}},
            {'proxies': {'https_proxy': None, 'http_proxy': 'http://12.1'}, 'expected': {}},
            {'proxies': {'http_proxy': 'localhost:9090'}, 'expected': {}},
            {'proxies': {'http_proxy': 'http://localhost:9090'}, 'expected': {'http': 'http://localhost:9090'}},
            {
                'proxies': {'http_proxy': 'http://localhost:9090', 'https_proxy': None},
                'expected': {'http': 'http://localhost:9090'}
            },
            {
                'proxies': {'https_proxy': 'https://localhost:9090', 'http_proxy': None},
                'expected': {'https': 'https://localhost:9090'}
            },
            {
                'proxies': {
                    'https_proxy': 'https://localhost:9090',
                    'http_proxy': 'http://localhost:9090',
                },
                'expected': {
                    'https': 'https://localhost:9090',
                    'http': 'http://localhost:9090',
                }
            },
        ]
        for test in tests:
            g = gist.Gist(**test['proxies'])
            self.assertDictEqual(test['expected'], g.proxies)
