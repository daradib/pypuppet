#!/usr/bin/env python

from distutils.core import setup

setup(name='pypuppet',
      version='0.1',
      description='Python wrapper for Puppet REST API',
      author='Dara Adib',
      author_email='daradib@kloudless.com',
      url='http://github.com/daradib/pypuppet',
      install_requires=['pyyaml', 'requests', 'requests_cache'],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Systems Administration',
      ],
      packages=['puppet'],
      )
