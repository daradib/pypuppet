import requests
import yaml


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
    def __init__(self, host, port, key_file, cert_file, ssl_verify,
        cache, cache_file, cache_backend, cache_expire_after):

        self.endpoint = 'https://' + host + ':' + str(port)
        self.key_file = key_file
        self.cert_file = cert_file
        self.ssl_verify = ssl_verify
        self.cache = cache
        self.cache_file = cache_file
        self.cache_backend = cache_backend
        self.cache_expire_after = cache_expire_after

    def get(self, resource, key='no_key', environment='production', parser='yaml'):
        """Query Puppet information using REST API and client SSL cert"""
        url = '/'.join((self.endpoint, environment, resource, key))
        if self.cache:
            import requests_cache
            _session = requests_cache.CachedSession(cache_name=self.cache_file,
                backend=self.cache_backend, expire_after=self.cache_expire_after)
        else:
            _session = requests.Session()

        _session.headers = {'Accept': parser}

        req = _session.get(url, cert=(self.cert_file, self.key_file), verify=self.ssl_verify)

        if req.status_code == 200:
            if parser == 'yaml':
                value = load_yaml(req.text)
            elif parser == 'pson':
                value = req.json()
            else:
                value = str(req.text).rstrip()
        else:
            raise APIError(req.text)

        return value

    def delete(self, resource, key='no_key', environment='production', parser='yaml'):
        """Delete entry from puppetserver"""
        url = '/'.join((self.endpoint, environment, resource, key))
        _session = requests.Session()
        req = _session.delete(url, cert=(self.cert_file, self.key_file), verify=self.ssl_verify)
        if req.status_code != 200:
            raise APIError(req.text)
