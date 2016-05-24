#!/usr/bin/env python

import argparse
import logging
import os
import json
import numpy

from osgeo import gdal, gdal_array
from ground_surveyor import my_progress_bar

    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('--measure', default='sharpness',
                         help='metadata measure to maximize')
    aparser.add_argument('dir', default='.',
                         help='Directory containing a set of unit field piles.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    mosaic_filename = os.path.join(args.dir,'mosaic_raw.tif')
    mosaic_ds_raw = gdal.GetDriverByName('GTiff').Create(
        mosaic_filename, 4096, 4096, 1, gdal.GDT_UInt16)
    mosaic_filename = os.path.join(args.dir,'mosaic_small.tif')
    mosaic_ds_small = gdal.GetDriverByName('GTiff').Create(
        mosaic_filename, 4096, 4096, 1, gdal.GDT_UInt16)
    mosaic_filename = os.path.join(args.dir,'mosaic_large.tif')
    mosaic_ds_large = gdal.GetDriverByName('GTiff').Create(
        mosaic_filename, 4096, 4096, 1, gdal.GDT_UInt16)



    file_list = os.listdir(args.dir)
    file_list_selected = []

    for filename in file_list:
        basename = os.path.basename(filename)
        if (basename.startswith('ufr_')) \
           and (basename.endswith('_metadata.json')):
            file_list_selected.append(filename)

    ## -- Initialize progress bar
    counter = 0L
    current_progress = my_progress_bar.progressBar(0, len(file_list_selected))

    for filename in file_list_selected:

        counter += 1
        current_progress.updateAmount_and_write_if_needed(counter)


        pile_name = '_'.join(filename.split('_')[1:3])

        file_path = os.path.join(args.dir, filename)

        pile_md = json.load(open(file_path))

#        print pile_name

        
        raw_filename = os.path.join(
            args.dir,
            'ufr_' + pile_name + '_medians.tif')

        raw = gdal_array.LoadFile(raw_filename)
#        print raw.shape
        best_img_raw   = raw[0] ## / numpy.median(raw[0])
        best_img_small = raw[1] ## / numpy.median(raw[0])
        best_img_large = raw[2] ## / numpy.median(raw[0])
        
        uf_i = int(pile_name.split('_')[0])
        uf_j = int(pile_name.split('_')[1])

        mosaic_ds_raw.GetRasterBand(1).WriteArray(
            best_img_raw, uf_i * 256, uf_j * 256)
        mosaic_ds_small.GetRasterBand(1).WriteArray(
            best_img_small, uf_i * 256, uf_j * 256)
        mosaic_ds_large.GetRasterBand(1).WriteArray(
            best_img_large, uf_i * 256, uf_j * 256)

    print 'See ', mosaic_filename

if __name__ == '__main__':
    main()
