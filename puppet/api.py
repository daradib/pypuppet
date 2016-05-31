import urllib2
import requests
import yaml
from httplib import HTTPSConnection
from json import load as load_json

class APIError(Exception):
    """Error returned by Puppet REST API"""
    pass

def load_yaml(stream):
    """Parse Puppet YAML into Python objects"""
    # Puppet YAML contains Ruby objects which need to be defined
    def construct_ruby_object(loader, suffix, node):
        return loader.construct_yaml_map(node)
    def construct_ruby_sym(loader, node):
        return loader.construct_yaml_str(node)
    yaml.add_multi_constructor('!ruby/object:', construct_ruby_object)
    yaml.add_constructor('!ruby/sym', construct_ruby_sym)
    try:
        document = yaml.load(stream)
    except yaml.loader.ConstructorError as e:
        if "unhashable type: 'list'" in str(e):
            raise NotImplementedError("http://pyyaml.org/ticket/169")
        else:
            raise
    return document

class Requestor(object):
    def __init__(self, host, port, key_file, cert_file, parser, ssl_verify):
        self.endpoint = 'https://' + host + ':' + str(port)
        self.key_file = key_file
        self.cert_file = cert_file
        self.parser = parser
        self.ssl_verify = ssl_verify
        self._session = requests.Session()
        self._session.headers = {
            'Accept':parser
        }
    def get(self, resource, key='no_key', environment='production'):
        """Query Puppet information using REST API and client SSL cert"""
        url = '/'.join((self.endpoint, environment, resource, key))

        try:
            req = self._session.get(url, cert=(self.cert_file, self.key_file), verify=self.ssl_verify)

            if req.status_code == 200:
                if self.parser == 'yaml':
                    value = load_yaml(req.text)
                elif self.parser == 'pson':
                    value = load_json(req.text)
                else:
                    value = req.text
            else:
                value = req.text
        except:
            pass

        return value
