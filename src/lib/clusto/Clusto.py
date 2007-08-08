
from clusto.drivers.Base import Thing
from clusto.schema import *


def flush():
    CTX.current.flush()


def getByName(name):
    return Thing.selectone(Thing.c.name == name)
                


