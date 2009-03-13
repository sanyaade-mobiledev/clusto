#!/usr/bin/env python
from clusto.scripthelpers import getClustoConfig
import clusto

from pprint import pprint
import sys

def print_tree(root, indent=0, attrs=['name']):
    for x in root.contents():
        txt = ''
        for attr in attrs:
            value = None

            if attr.startswith('.'):
                attr = attr.lstrip('.')
                method = getattr(x, attr, None)
                if method and callable(method):
                    value = method()

                if not value:
                    try:
                        value = eval('%s(x)' % attr)
                    except:
                        value = None

            if not value:
                value = getattr(x, attr, None)

            if not value:
                value = [i.value for i in x.attrQuery(key=attr)]
                if len(value) == 1:
                    value = value[0]

            if not value:
                value = None
            txt += '%s: %s\t' % (attr, value)

        print '\t' * indent, txt
        print_tree(x, indent=(indent + 1), attrs=attrs)

def main():
    if len(sys.argv) < 2:
        print 'Usage: %s <object name> [attributes...]' % sys.argv[0]
        sys.exit(0)

    if len(sys.argv) > 2:
        attrs = sys.argv[2:]
    else:
        attrs = ['name']

    print_tree(clusto.getByName(sys.argv[1]), attrs=attrs)

if __name__ == '__main__':
    config = getClustoConfig()
    clusto.connect(config.get('clusto', 'dsn'))
    #clusto.initclusto()
    main()
