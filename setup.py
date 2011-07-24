#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Clusto cluster management tool
# Copyright 2009, Ron Gorodetzky ron@parktree.net

import os
import setuptools
import sys


srcdir = os.path.join(os.path.dirname(sys.argv[0]), 'src')

setuptools.setup(
    name = "clusto",
    version = "0.6.0-dev",
    packages = setuptools.find_packages('src'),
    author = "Ron Gorodetzky",
    author_email = "ron@parktree.net",
    description = "Cluster management and inventory system",
    install_requires = [
        'argparse',
        'sqlalchemy>=0.6.3,<0.7',
        'IPython',
        'scapy',
        'IPy',
        'epydoc',
        'sphinx',
        'PyYAML',
        'WebOb',
        'mako',
        'boto>=2.0',
        'kombu',
    ],
    entry_points = {
        'console_scripts': [
            'clusto = clusto.script_helper:main',
            'clusto-allocate = clusto.commands.allocate:main',
            'clusto-attr = clusto.commands.attr:main',
            'clusto-console = clusto.commands.console:main',
            'clusto-deallocate = clusto.commands.deallocate:main',
            'clusto-fai = clusto.commands.fai:main',
            'clusto-info = clusto.commands.info:main',
            'clusto-list-pool = clusto.commands.list_pool:main',
            'clusto-pool = clusto.commands.pool:main',
            'clusto-puppet-node = clusto.commands.puppet_node:main',
            'clusto-reboot = clusto.commands.reboot:main',
            'clusto-shell = clusto.commands.shell:main',
        ],
    },
    zip_safe = False,
    package_dir = { '': 'src' },
    scripts = [
        os.path.join(srcdir, 'scripts', 'clusto-dhcpd'),
        os.path.join(srcdir, 'scripts', 'clusto-kvm'),
        os.path.join(srcdir, 'scripts', 'clusto-httpd'),
        os.path.join(srcdir, 'scripts', 'clusto-mysql'),
        os.path.join(srcdir, 'scripts', 'clusto-hadoop-node'),
        os.path.join(srcdir, 'scripts', 'clusto-snmptrapd'),
        os.path.join(srcdir, 'scripts', 'clusto-tree'),
        os.path.join(srcdir, 'scripts', 'clusto-update-info'),
        os.path.join(srcdir, 'scripts', 'clusto-barker-consumer'),
        os.path.join(srcdir, 'scripts', 'clusto-puppet-node2'),
        os.path.join(srcdir, 'scripts', 'clusto-update-db'),
        #os.path.join(srcdir, 'scripts', 'clusto-vm'),
      ],
      test_suite = "clusto.test.alltests.gettests",
      dependency_links = [ 'http://www.secdev.org/projects/scapy/' ]
)

