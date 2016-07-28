#!/usr/bin/env python

import argparse
import logging
import os

from ground_surveyor import uf_statistics

    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('--stat', default='variance',
                         choices = ['variance'],
                         help='statistic to compute')
    aparser.add_argument('dir', default='.',
                         help='Directory containing a set of unit field piles.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)


    filename = uf_statistics.statistics_metatile(
        args.dir, 
        args.stat,
        processing_options = {
            },
        )


if __name__ == '__main__':
    main()
