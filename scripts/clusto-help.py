#!/usr/bin/env python

import sys
import clusto.scripthelpers


def main(argv):

    helpmsg = ["Available Commands:"]

    scripts = set()

    for i in clusto.scripthelpers.scriptpaths:
        scripts.update(map(lambda s: s.split('-')[1].split('.')[0],
                           clusto.scripthelpers.listClustoScripts(i)))

    helpmsg.extend(sorted(scripts))

    print
    print '\n\t'.join(helpmsg)
    print
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
