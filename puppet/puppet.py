from .api import Requestor
from .node import Node


class Puppet(object):
    """Python wrapper for Puppet REST API"""

    def __init__(self, host='localhost', port=8140, key_file=None,
        cert_file=None, ssl_verify=True, cache_enabled=True,
        cache_file='/tmp/pypuppet_cache', cache_backend='sqlite', cache_expire_after=3600):

        self.requestor = Requestor(host=host, port=port, key_file=key_file,
            cert_file=cert_file, ssl_verify=ssl_verify, cache=cache_enabled,
            cache_file=cache_file, cache_backend=cache_backend,
            cache_expire_after=cache_expire_after)

    def certificates(self):
        """List certnames of known SSL certificates"""
        certnames = []
        for cert in self.requestor.get('certificate_statuses', 'no_key'):
            certnames.append(cert['name'])
        return certnames

    def certificate_requests(self):
        """List certnames of SSL certificate requests"""
        certnames = []
        for cert in self.requestor.get('certificate_requests', 'no_key'):
            certnames.append(cert['name'])
        return certnames

    # TODO: Need to use REST API instead of subprocess call on puppetmaster
    # def clean_node(requestor, certname):
    #     """Revoke certificate and remove knowledge of a Puppet node"""
    #     return subprocess.check_call(['puppet', 'node', 'clean', certname])

    def facts_search(self, *args):
        """List nodes matching matching arguments of fact comparisons"""
        if args is None:
            return self.requestor.get('facts_search', 'no_key')
        query = []
        for term in args:
            if len(term) == 2:
                fact, value = term
                comparison = 'eq'
            elif len(term) == 3:
                fact, comparison, value = term
            else:
                raise ValueError("facts_search term should have 2 or 3 elements")
            query.append('facts.' + fact + '.' + comparison + '=' + str(value))
        return str(self.requestor.get('facts_search', 'search?' + '&'.join(query)))

    def node(self, certname, environment='production'):
        """Create Puppet Node object"""
        return Node(self.requestor, certname=certname, environment=environment)
