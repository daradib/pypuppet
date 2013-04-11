# pypuppet

Python wrapper for Puppet REST API

This module wraps the [Puppet REST API](http://docs.puppetlabs.com/guides/rest_api.html) to make it easier for Python scripts to integrate with Puppet. Lazy evaluation and memoization is used to reduce calls to the API.

Testing, feedback, and pull requests are welcome.

Kudos to my employer, [Kloudless](http://kloudless.com/), for giving me permission to publish this.

## Usage

    > import puppet
    > p = puppet.Puppet(host='puppet.example.com', key_file='api-key.pem',
          cert_file='api-cert.pem')

Replace puppet.example.com with the hostname of the puppet master and api-key.pem/api-cert.pem with the client SSL key/certificate files.

### Node object

    > n = p.node('magicsmoke.example.com')
    > print dir(n)
    ['__doc__', '__init__', '__module__', 'catalog', 'certificate',
    'certificate_status', 'certname', 'classes', 'environment', 'facts',
    'node', 'parameters', 'report', 'requestor']

Replace magicsmoke.example.com with the certname of a puppet node.

Each Node object consists of attributes, lazy-evaluated attributes, and methods.

Attributes:
 * `certname`: `'magicsmoke.example.com'`
 * `classes`: `['common', 'ntp']`
 * `environment`: `'production'`
 * `facts`: `{...}`
 * `node`: `{...}`
 * `parameters`: `{...}`

Lazy-evaluated attributes:
 * `certificate`: `'-----BEGIN CERTIFICATE-----...'`
 * `certificate_status`: `'signed'`

Methods:
 * `catalog()`: `{...}` (compiles and downloads catalog)

### Methods

In addition to the Node class, there are two methods in the Puppet object:
 * `facts_search`: list certnames matching arguments of fact comparisons
 * `list_nodes`: list all known certnames based on signed certificates and cached facts

Note that these methods return lists of certname strings, not lists of Node objects (which would be an expensive API call).

Each argument of facts_search must have two or three elements. The first argument is the name of the fact and the last argument is the string for comparison. If three arguments are provided, the second argument is the comparison type. The arguments are combined with boolean AND. Refer to the Puppet REST API documentation on [facts search](http://docs.puppetlabs.com/guides/rest_api.html#facts-search).

    > print p.facts_search(('architecture', 'amd64'),('osfamily', 'Debian'))
    [...]
    > print p.facts_search(('uptime_days', 'gt', '30'))
    [...]

## Getting started

Install the module using pip.

    $ pip install https://github.com/daradib/pypuppet/archive/master.tar.gz

Alternatively, you can move the puppet directory to your Python PATH or wherever a script that imports it will be located. The only dependency is [PyYAML](http://pyyaml.org/).

The module defaults to using a SSL key and certificate called puppet in `/var/lib/puppet/ssl`. You will probably want to create and use a different certificate. On the puppet master:

    $ sudo puppet cert generate api

Replace api with another certname if desired.

This will generate `$vardir/ssl/private_keys/api.pem` and `$vardir/ssl/certs/api.pem`, which should be moved or otherwise made accessible to the user and host using pypuppet, if necessary. On Debian, `$vardir` defaults to `/var/lib/puppet`.

To allow access to the REST API using the generated SSL key/certificate, the puppet master [auth.conf](http://docs.puppetlabs.com/guides/rest_auth_conf.html) file needs to be changed. `auth.conf.example` is included in this directory as an example.

## Caveats

Bugs:
 * Memoization is rudimentary. Stale information is kept indefinitely (in the current Python process).
 * There is no verification of the server SSL certificate.

Not currently supported:
 * PUT requests (sending and signing certificate requests, sending facts and reports, putting files in the file bucket) and DELETE requests (revoking certificate requests)
 * puppet agent API

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
