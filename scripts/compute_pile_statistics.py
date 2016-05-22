#!/usr/bin/env python

import argparse
import logging
import os
import datetime

from ground_surveyor import my_progress_bar
from ground_surveyor import uf_analyse

    
def process_pile(out_basename, raw_pile):

    dc = uf_analyse.load_pile(raw_pile)
    uf_analyse.compute_median(dc)
    uf_analyse.analyse_pile(dc)
    uf_analyse.compute_spatial_cross_correlations(dc)
    uf_analyse.save_statistics(dc, out_basename)

    
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



    # Filter the list of filenames to keep only those with relevant piles. There
    # is some redundancy with what is done just above in the case of an entire
    # directory passed to the program as an argument. This could be written better,

    my_pile_list = []
    for filename in args.piles:
        basename = os.path.basename(filename)
        if (basename.startswith('uf_')) \
           and (basename.endswith('_raw.tif')):
            my_pile_list.append(filename)


    ## -- Initialize progress bar
    counter = 0L
    current_progress = my_progress_bar.progressBar(0, len(my_pile_list))
    print 'Start time:',datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    print 'Found ',len(my_pile_list),' piles of unit fields. Expected: 256 for a whole metatile.'
    
    for filename in my_pile_list:
        
        counter += 1
        current_progress.updateAmount_and_write_if_needed(counter)

        basename = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        if dirname == '':
            dirname = '.'
            
        pile_name = '_'.join(basename.split('_')[1:3])
        process_pile('%s/ufr_%s' % (dirname, pile_name),
                     filename)

    print 'End time:',datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    

if __name__ == '__main__':
    main()
