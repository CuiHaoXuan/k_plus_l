#!/usr/bin/python

"""
Help on method lognormvariate in module random:

lognormvariate(self, mu, sigma) method of random.Random instance
    Log normal distribution.

    If you take the natural logarithm of this distribution, you'll get a
    normal distribution with mean mu and standard deviation sigma.
    mu can have any value, and sigma must be greater than zero.

Sample run of this script:
python log_normal.py -m 1 -d 2

"""

import random
from optparse import OptionParser
import sys

def lognorm(mean, std):
    ''' generate random numbers for log normal distribution '''
    load = random.lognormvariate(mean, std)
    return load

def create_option(parser):
    ''' add the options to the parser '''
    parser.add_option("-v", action="store_true",
                        dest="verbose",
                        help="print output to screen")
    parser.add_option("-m", dest="mean_val",
                      type="int",
                      default=1,
                      help="the mean value of log normal distribution")
    parser.add_option("-d", dest="std_val",
                      type="float",
                      default=0.5,
                      help="the standard deviation of the log normal distribution")

def main(argv=None):
    ''' program wrapper '''
    if not argv:
        argv=sys.argv[1:]
    usage = ("""%prog [-v verbose] [-m mean] [-d standard deviation]""")
    parser = OptionParser(usage=usage)
    create_option(parser)
    (options, _) = parser.parse_args(argv)

    # take argument
    mean_val = options.mean_val
    std_val = options.std_val
    load = lognorm(mean_val, std_val)
    print load

if __name__ == '__main__':
    sys.exit(main())
