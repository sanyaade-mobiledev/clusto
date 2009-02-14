from clusto.scripthelpers import getClustoConfig
import clusto
import sys

def print_tree(root, indent=0, attrs=['name']):
    for x in root.contents():
        txt = ''
        for attr in attrs:
            txt += '%s: %s\t' % (attr, getattr(x, attr, 'None'))

        print '\t' * indent, txt
        print_tree(x, indent=(indent + 1), attrs=attrs)

def main():
    if len(sys.argv) < 2:
        print 'Usage: %s <object name> [attributes...]' % sys.argv[0]

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
