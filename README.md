# pypuppet

Python wrapper for Puppet REST API

This package wraps the [Puppet REST API](http://docs.puppetlabs.com/guides/rest_api.html) to make it easier for Python scripts to integrate with Puppet. Lazy evaluation and memoization is used to reduce calls to the API.

Testing, feedback, and pull requests are welcome.

Kudos to my employer, [Kloudless](http://kloudless.com/), for giving me permission to publish this.

## Usage

    >>> import puppet
    >>> p = puppet.Puppet()

By default, the Puppet instance will use an unauthenticated SSL connection to localhost. A better example would be to use client authentication.

    >>> p = puppet.Puppet(host='puppet.example.com', port=8140,
    ... key_file='api-key.pem', cert_file='api-cert.pem')

Replace puppet.example.com with the hostname of the puppet master and api-key.pem/api-cert.pem with the client SSL key/certificate files.

### Node object

Given a puppet node called magicsmoke.example.com,

    >>> n = p.node('magicsmoke.example.com')
    >>> str(n)
    'magicsmoke.example.com'
    >>> dir(n)
    ['__doc__', '__init__', '__module__', '__str__', 'catalog', 'certificate', 'certificate_status', 'certname', 'classes', 'environment', 'facts', 'node', 'parameters', 'requestor']

An optional node environment argument can be provided. Note that [external node classifiers](http://docs.puppetlabs.com/guides/external_nodes.html) may [override the requested environment](http://docs.puppetlabs.com/guides/environment.html#in-an-enc).

    >>> n_dev = p.node('magicsmoke.example.com', environment='dev')

If a node is not found, `puppet.APIError` will be raised.

#### `certname`

    >>> n.certname
    'magicsmoke.example.com'

#### `classes`

    >>> type(n.classes)
    <type 'list'>

#### `environment`

    >>> n.environment
    'production'

#### `facts`

    >>> type(n.facts)
    <type 'dict'>
    >>> n.facts['osfamily'] + "-" + n.facts['architecture']
    'Debian-amd64'

#### `node`

    >>> type(n.node)
    <type 'dict'>
    >>> sorted(n.node.keys())
    ['classes', 'environment', 'expiration', 'facts', 'name', 'parameters', 'time']

#### `parameters`

    >>> type(n.parameters)
    <type 'dict'>

#### `certificate`
*lazy-evaluated*

    >>> type(n.certificate)
    <type 'str'>
    >>> n.certificate.startswith('-----BEGIN CERTIFICATE')
    True

#### `certificate_status`
*lazy-evaluated*

    >>> n.certificate_status
    'signed'

#### `catalog`
*method* (compiles and downloads catalog)

    >>> catalog = n.catalog()
    >>> type(catalog)
    <type 'dict'>
    >>> sorted(catalog.keys())
    [u'classes', u'edges', u'environment', u'name', u'resources', u'tags', u'version']

### Methods

In addition to the node method which creates a Node instance, there are three other methods in the Puppet instance.

 * `certificates`: list certnames of known SSL certificates
 * `certificate_requests`: list certnames of SSL certificate requests
 * `facts_search`: list nodes matching arguments of fact comparisons

Note that these methods return lists of strings, not lists of Node objects (which would be an expensive API call). 

    >>> [type(certnames[0]) for certnames in (p.certificates(),
    ... p.facts_search())]
    [<type 'str'>, <type 'str'>]

However, each string can be directly passed as the argument to the node method to create a Node object. A `try-except` code block is recommended to gracefully handle exceptions caused by non-existent nodes.

    >>> for certname in p.certificates():
    ...     try:
    ...         n_ = p.node(certname)
    ...         break
    ...     except puppet.APIError:
    ...         # node probably does not exist
    ...         continue
    >>> dir(n_) == dir(n)
    True

Each argument (if provided) of `facts_search` must have two or three elements. The first argument is the name of the fact and the last argument is the string for comparison. If three arguments are provided, the second argument is the comparison type. The arguments are combined with boolean AND. Refer to the Puppet REST API documentation on [facts search](http://docs.puppetlabs.com/guides/rest_api.html#facts-search).

    >>> if p.facts_search(('architecture', 'amd64'),('osfamily', 'Debian')):
    ...     print True
    True
    >>> long_running_servers = p.facts_search(('uptime_days', 'gt', '100'))

### Requestor object

Direct invocation of the API can be done using the Requestor object's `get` method, which takes four arguments:

 * `resource` (required)
 * `key` (default: `'no_key'`)
 * `environment` (default: `'production'`)
 * `parser`: `yaml` (default), `pson`, or `s`

For example:

    >>> crl = p.requestor.get('certificate_revocation_list', 'ca', parser='s')
    >>> type(crl)
    <type 'str'>
    >>> crl.startswith('-----BEGIN X509 CRL')
    True

Some other examples based on the [Puppet REST API documentation](http://docs.puppetlabs.com/guides/rest_api.html):

    p.requestor.get('resource', 'package/puppet')
    p.requestor.get('resources', 'user')

## Getting started

Install the module using pip.

    $ pip install https://github.com/daradib/pypuppet/archive/master.tar.gz

Alternatively, you can move the puppet directory to your Python PATH or wherever a script that imports it will be located. The only dependency is [PyYAML](http://pyyaml.org/).

The module defaults to using an unauthenticated SSL connection. You may want to create and use a client SSL key/certificate signed by the Puppet CA. On the puppet master (with root privileges):

    $ puppet cert generate api

Replace api with another certname if desired.

This will generate `$vardir/ssl/private_keys/api.pem` and `$vardir/ssl/certs/api.pem`, which should be moved or otherwise made accessible to the user and host using pypuppet, if necessary. On Debian, `$vardir` defaults to `/var/lib/puppet`.

To allow access to the REST API, the puppet master [auth.conf](http://docs.puppetlabs.com/guides/rest_auth_conf.html) file needs to be changed. `auth.conf.example` is included in this directory as an example.

## Caveats

Bugs:

 * Memoization is rudimentary. Stale information is kept indefinitely (in the current Python process).
 * There is no verification of the server SSL certificate.

Not currently supported:

 * PUT requests (sending and signing certificate requests, sending facts and reports, putting files in the file bucket) and DELETE requests (revoking certificate requests)

## Author

[Dara Adib](http://github.com/daradib/) for [Kloudless, Inc.](http://kloudless.com/)

## License

Copyright 2012-2013 Kloudless, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
