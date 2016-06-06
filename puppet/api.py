import urllib2
import requests
import yaml
from httplib import HTTPSConnection

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
    def __init__(self, host, port, key_file, cert_file, ssl_verify):
        self.endpoint = 'https://' + host + ':' + str(port)
        self.key_file = key_file
        self.cert_file = cert_file
        self.ssl_verify = ssl_verify

    def get(self, resource, key='no_key', environment='production', parser='yaml'):
        """Query Puppet information using REST API and client SSL cert"""
        url = '/'.join((self.endpoint, environment, resource, key))
        _session = requests.Session()
        _session.headers = {
            'Accept':parser
        }

        try:
            req = _session.get(url, cert=(self.cert_file, self.key_file), verify=self.ssl_verify)

            if req.status_code == 200:
                if parser == 'yaml':
                    value = load_yaml(req.text)
                elif parser == 'pson':
                    value = req.json()
                else:
                    value = str(req.text).rstrip()
            else:
                value = req.text
        except:
            value = req.text

        return value
