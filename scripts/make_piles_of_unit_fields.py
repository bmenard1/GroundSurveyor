#!/usr/bin/env python

import argparse
import logging

from ground_surveyor import uf_creator

    
def main():
    aparser = argparse.ArgumentParser(
        description='Split metatile stack into unit fields.')

    aparser.add_argument('-o', '--output-dir', default='.',
                         help='Directory to put unit fields in.')
    aparser.add_argument('metatiles', nargs='*',
                         help='Input metatiles')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    uf_creator.split_metatiles(args.output_dir, args.metatiles)
        

if __name__ == '__main__':
    main()
