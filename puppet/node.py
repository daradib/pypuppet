from .utils import Lazy, Memoize

@Memoize
class Node:
    """Puppet Node object with some lazy-evaluated attributes"""

    def __init__(self, requestor, certname, environment=None):
        self.requestor = requestor
        if environment is None:
            # Use the default production environment because the node dict
            # is not apparently dependent on the environment we specify,
            # perhaps because of the ENC
            node = self.requestor.get('node', certname, environment='production')
            environment = node['environment']
        else:
            node = self.requestor.get('node', certname, environment=environment)
        self.certname = certname
        self.environment = environment
        self.node = node
        self.classes = node['classes']
        self.facts = node['facts']['values']
        self.parameters = node['parameters']

    def catalog(self):
        """Compile and download the node's catalog"""
        # Catalog is not parsable by PyYAML, use JSON instead
        return self.requestor.get(
            'catalog', self.certname, environment=self.environment,
            parser='pson')['data']

    @Lazy
    def certificate(self):
        return str(self.requestor.get(
            'certificate', self.certname, environment=self.environment,
            parser='s'))

    @Lazy
    def certificate_status(self):
        # YAML output is not as useful as PSON
        return str(self.requestor.get('certificate_status', self.certname,
            environment=self.environment, parser='pson')['state'])

    # TODO: Need to use REST API instead of looking at files on puppetmaster
    # Unfortunately, REST API only supports PUT for reports, not GET
    # @Lazy
    # def report(self):
    #     # Puppet API does not implement getting reports, use local disk
    #     path = '/'.join(('/var/lib/puppet', 'reports', self.certname))
    #     if os.path.isdir(path):
    #         filename = sorted(os.listdir(path))[-1]
    #         filepath = os.path.join(path, filename)
    #         with open(filepath) as f:
    #             report = load_yaml(f)
    #         return report
    #     else:
    #         # Reports directory does not exist, no reports yet
    #         return None
