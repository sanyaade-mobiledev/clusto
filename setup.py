#!/usr/bin/env python
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8
#
# Clusto cluster management tool
# Copyright 2009, Ron Gorodetzky ron@fflick.com

import os
import setuptools
import sys

srcdir = os.path.join(os.path.dirname(sys.argv[0]), 'src')

setuptools.setup(
    name = "clusto",
    version = "0.6.0",
    packages = setuptools.find_packages(srcdir),
    author = "Ron Gorodetzky",
    author_email = "ron@fflick.com",
    description = "Cluster management and inventory system",
    install_requires = [
        'argparse',
        'sqlalchemy>=0.6.4',
        'IPython',
        'scapy',
        'IPy',
    ],
    entry_points = {
        'console_scripts': [
            'clusto = clusto.script_helper:main',
            'clusto-shell = clusto.commands.shell:main',
            'clusto-info = clusto.commands.info:main',
            'clusto-pool= clusto.commands.pool:main',
            'clusto-list-pool= clusto.commands.list_pool:main',
        ],
    },
    zip_safe = False,
    package_dir = { '': srcdir },
    scripts = [
        #os.path.join(srcdir, 'scripts', 'clusto-allocate'),
        #os.path.join(srcdir, 'scripts', 'clusto-attr'),
        #os.path.join(srcdir, 'scripts', 'clusto-console'),
        #os.path.join(srcdir, 'scripts', 'clusto-dhcpd'),
        #os.path.join(srcdir, 'scripts', 'clusto-fai'),
        #os.path.join(srcdir, 'scripts', 'clusto-kvm'),
        #os.path.join(srcdir, 'scripts', 'clusto-httpd'),
        #os.path.join(srcdir, 'scripts', 'clusto-mysql'),
        #os.path.join(srcdir, 'scripts', 'clusto-puppet-node'),
        #os.path.join(srcdir, 'scripts', 'clusto-hadoop-node'),
        #os.path.join(srcdir, 'scripts', 'clusto-reboot'),
        #os.path.join(srcdir, 'scripts', 'clusto-snmptrapd'),
        #os.path.join(srcdir, 'scripts', 'clusto-tree'),
        #os.path.join(srcdir, 'scripts', 'clusto-update-info'),
        #os.path.join(srcdir, 'scripts', 'clusto-vm'),
        #os.path.join(srcdir, 'scripts', 'clusto-deallocate'),
      ],
      test_suite = "clusto.test.alltests.gettests",
      dependency_links = [ 'http://www.secdev.org/projects/scapy/' ]
)

