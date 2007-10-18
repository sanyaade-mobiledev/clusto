
from setuptools import setup, find_packages

setup(
    name = "Clusto",
    version = "0.1",
    packages = find_packages(),
    author = "Ron Gorodetzky",
    author_email = "ron@digg.com",
    description = "Clusto, cluster management and inventory system",
    scripts = ['./clusto.py'],
    test_suite = "test.alltests"
    )


