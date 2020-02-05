import json
import os
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback


class Response(object):
    def __init__(self, resp, info):
        self.resp = resp
        self.info = info
        if "body" in info:
            self.json_body = self.info["body"]

    @property
    def status_code(self):
        return self.info["status"]

    @property
    def json(self):
        try:
            return json.loads(to_text(self.json_body))
        except:
            return None
        

class QuayHelper:

    def __init__(self, module, token, endpoint):
        self.module = module
        self.endpoint = endpoint
        self.timeout = module.params.get('timeout', 30)
        self.headers = {'Authorization': 'Bearer {0}'.format(token),
                        'Content-type': 'application/json'}

        # Check if api_token is valid or not
        response = self.get('/api/v1/superuser/users/')
        if response.status_code == 401:
            self.module.fail_json(msg='Failed to login using API token, please verify validity of API token.')

    def _url_builder(self, path):
        return 'https://%s%s' % (self.endpoint, path)

    def send(self, method, path, data=None):
        url = self._url_builder(path)
        data = self.module.jsonify(data)
        resp, info = fetch_url(self.module, url, data=data, headers=self.headers, method=method, timeout=self.timeout)
        return Response(resp, info)

    def get(self, path, data=None):
        return self.send('GET', path, data)

    def put(self, path, data=None):
        return self.send('PUT', path, data)

    def post(self, path, data=None):
        return self.send('POST', path, data)

    def delete(self, path, data=None):
        return self.send('DELETE', path, data)
