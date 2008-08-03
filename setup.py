
import glob
import os
import sys

from setuptools import setup, find_packages

srcdir = os.path.dirname(sys.argv[0])

setup(
    name = "Clusto",
    version = "0.1.1",
    packages = find_packages('lib'),
    author = "Ron Gorodetzky",
    author_email = "ron@digg.com",
    description = "Clusto, cluster management and inventory system",
    install_requires = ['sqlalchemy>=0.5.0beta2'],
    package_dir = {'':'lib'},
    scripts=glob.glob(os.path.join(srcdir, 'scripts', 'clusto')),
    test_suite = "clusto.test.alltests.gettests"
    )


