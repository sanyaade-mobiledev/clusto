
import glob
import os
import sys

from setuptools import setup, find_packages

srcdir = os.path.join(os.path.dirname(sys.argv[0]), 'src')

setup(name = "clusto",
      version = "0.3.0",
      packages = find_packages('src'),
      author = "Ron Gorodetzky",
      author_email = "ron@digg.com",
      description = "Clusto, cluster management and inventory system",
      install_requires = ['sqlalchemy>=0.5.0', 'IPy>=0.55', 'IPython'],
      package_dir = {'':'src'},
      #scripts=glob.glob(os.path.join(srcdir, 'scripts', 'clusto')),
      scripts=[os.path.join(srcdir, 'scripts', 'clusto'), 
               os.path.join(srcdir, 'scripts', 'clusto-shell'), 
               os.path.join(srcdir, 'scripts', 'clusto-info'), 
               os.path.join(srcdir, 'scripts', 'clusto-help'), 
               os.path.join(srcdir, 'scripts', 'clusto-puppet'), 
               os.path.join(srcdir, 'scripts', 'clusto-fai'), 
               os.path.join(srcdir, 'scripts', 'clusto-tree'),
               os.path.join(srcdir, 'scripts', 'clusto-console'),
               os.path.join(srcdir, 'scripts', 'clusto-pool-members'),
               ],
      test_suite = "clusto.test.alltests.gettests"
      )


