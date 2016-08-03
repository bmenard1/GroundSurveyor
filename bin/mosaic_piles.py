#!/usr/bin/env python

import argparse
import logging
import os

from ground_surveyor import uf_mosaic

    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('--measure', default='normalized_sharpness',
                         help='metadata measure to maximize')
    aparser.add_argument('dir', default='.',
                         help='Directory containing a set of unit field piles.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)


    mosaic_filename = uf_mosaic.mosaic_metatile(
        args.dir, 
        selection_options = {
            'order_field': args.measure,
            'cross_correlation_threshold': 0.25,
            'small_cross_correlation_threshold': 0.30,
            'zero_threshold': 0,
            },
        processing_options = {
            'normalize_intensity': True,
            },
        )


if __name__ == '__main__':
    main()
