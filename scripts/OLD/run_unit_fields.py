#!/usr/bin/env python

import argparse
import logging
import os

from ground_surveyor import analyse_unit_field_pile
from ground_surveyor import my_progress_bar
from ground_surveyor import analyse_unit_field_pile as uf_analyse

    
def process_pile(out_basename, raw_pile):
    dc = uf_analyse.load_pile(raw_pile)
    uf_analyse.analyse_pile(dc)
    uf_analyse.compute_median(dc)
    uf_analyse.compute_spatial_cross_correlations(dc)
    uf_analyse.save_pile(dc, out_basename)
    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('piles', default='.', nargs='+',
                         help='Pile(s) to process.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    # As a special hack, if a single directory is provided, we will scan
    # it for all piles.
    if len(args.piles) == 1 and os.path.isdir(args.piles[0]):
        dirname = args.piles[0]
        args.piles = []
        for filename in os.listdir(dirname):
            if filename.startswith('uf_') and filename.endswith('_raw.tif'):
                args.piles.append('%s/%s', dirname, filename)
    
    
    ## -- Initialize progress bar
    counter = 0L
    current_progress = my_progress_bar.progressBar(0, len(args.piles))

    for filename in args.piles:

        counter += 1
        current_progress.updateAmount_and_write_if_needed(counter)

        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        if dirname == '':
            dirname = '.'

        if (not basename.startswith('uf_')) \
           or (not basename.endswith('_raw.tif')):
            logging.warning('%s does not look like a pile, skipping.',
                            filename)
            continue

            
        pile_name = '_'.join(basename.split('_')[1:3])
#        print pile_name

        process_pile('%s/ufr_%s' % (dirname, pile_name),
                     filename)

        
    

if __name__ == '__main__':
    main()
