#!/usr/bin/env python

import argparse
import logging
import os

from ground_surveyor import analyse_unit_field_pile
from ground_surveyor import analyse_unit_field_pile as uf_analyse

    
def process_pile(filelist):
    dc = uf_analyse.load_pile(filelist)
    uf_analyse.analyse_pile(dc)
    uf_analyse.compute_median(dc)
    uf_analyse.compute_spatial_cross_correlations(dc)
    uf_analyse.save_pile(dc)
    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('dir', default='.',
                         help='Directory containing a set of unit field piles.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    piles = {}
    file_list = os.listdir(args.dir)
    for filename in file_list:
        if (not filename.startswith('uf_')) or (not filename.endswith('.tif')):
            continue

        pile_name = '_'.join(filename.split('_')[1:3])

        if pile_name not in piles.keys():
            piles[pile_name] = []

        piles[pile_name].append(os.path.join(args.dir,filename))

    for pile_name in piles.keys():
        print pile_name, len(piles[pile_name])

        process_pile(piles[pile_name])

        
    

if __name__ == '__main__':
    main()
