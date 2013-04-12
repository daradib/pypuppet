from .api import Requestor
from .node import Node, facts_search, list_nodes

class Puppet(object):
    """Python wrapper for Puppet REST API"""
    def __init__(self, host='localhost', port=8140, key_file=None,
        cert_file=None):
        self.requestor = Requestor(host=host, port=port, key_file=key_file, 
            cert_file=cert_file)
    def node(self, certname, environment=None):
        """Puppet Node object with some lazy-evaluated attributes"""
        return Node(self.requestor, certname=certname, environment=environment)
    def facts_search(self, *args):
        """List certnames matching matching arguments of fact comparisons"""
        return facts_search(self.requestor, *args)
    def list_nodes(self):
        """List certnames based on signed certificates and cached facts"""
        return list_nodes(self.requestor)
