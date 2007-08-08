

from clusto.schema import *
from clusto.drivers.Base import *


def flush():
    CTX.current.flush()


def getByName(name):
    return Thing.selectone(Thing.c.name == name)
