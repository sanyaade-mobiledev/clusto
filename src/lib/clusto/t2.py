
import sys
import schema
import drivers
from Clusto import Clusto

schema.metadata.connect('sqlite:///:memory:')
schema.metadata.create_all()

t=drivers.Thing('foo')
t.addAttr('key', 1)
t.addAttr('key', 2)

print t.getAttr('key', justone=False)

s=drivers.Server('myserver')
s.addAttr('vendor', 'pie')


s1=drivers.Server('myserver2')
s1.addAttr('vendor', 'pie2')

s2=drivers.Server('myserver3')
s2.addAttr('vendor', 'pie3')

s3=drivers.Server('myserver4')
s3.addAttr('vendor', 'pie')
s3.addAttr('stat', 'fast')

t.connect(s)
t.connect(s1)
t.connect(s2)
t.connect(s3)

Clusto.save()

conn = t.getConnectedMatching({'vendor': ['pie']})

print conn



