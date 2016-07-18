import urllib2
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

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    """urllib2 does not natively support HTTPS client authentication"""
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
    def https_open(self, req):
        return self.do_open(self.getConnection, req)
    def getConnection(self, host, timeout=300):
        return HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

class Requestor(object):
    def __init__(self, host, port, key_file, cert_file):
        self.endpoint = 'https://' + host + ':' + str(port)
        self.opener = urllib2.build_opener(HTTPSClientAuthHandler(
            key_file, cert_file))
    def get(self, resource, key='no_key', environment='production', parser='yaml'):
        """Query Puppet information using REST API and client SSL cert"""
        url = '/'.join((self.endpoint, environment, resource, key))
        request = urllib2.Request(url)
        request.add_header('Accept', parser)
        try:
            try:
                response = self.opener.open(request)
            except urllib2.HTTPError as e:
                    raise APIError((str(e) + ": " + url))
            if parser == 'yaml':
                value = load_yaml(response)
            elif parser == 'pson':
                value = load_json(response)
            else:
                value = response.read()
        finally:
            try:
                response.close()
            except NameError:
                # HTTPError would be raised, don't preempt it
                pass
        return value
    def delete(self, resource, key='no_key', environment='production', parser='yaml'):
        """Delete entry from puppetserver"""
        url = '/'.join((self.endpoint, environment, resource, key))
        request = urllib2.Request(url)
        request.add_header('Accept', parser)
        request.get_method = lambda: 'DELETE'
        try:
            try:
                response = self.opener.open(request)
            except urllib2.HTTPError as e:
                    raise APIError((str(e) + ": " + url))
        finally:
            try:
                response.close()
            except NameError:
                # HTTPError would be raised, don't preempt it
                pass

