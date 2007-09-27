#!/usr/bin/env python

import sys
import clusto


def main(argv):

    for i in clusto.DRIVERLIST:
        print i

        
if __name__ == "__main__":
    sys.exit(main(sys.argv))
