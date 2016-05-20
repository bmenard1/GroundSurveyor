#!/usr/bin/env python

import argparse
import logging
import os

from ground_surveyor import analyse_unit_field_pile as uf_analyse


def process_pile(filelist):
    dc = uf_analyse.load_pile(filelist)
    uf_analyse.analyse_pile(dc)
    uf_analyse.compute_median(dc)
    uf_analyse.save_pile(dc)
    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('unitfields', nargs='*',
                         help='All the unit field tiff files for one stack.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    process_pile(args.unitfields)
        
    

if __name__ == '__main__':
    main()

