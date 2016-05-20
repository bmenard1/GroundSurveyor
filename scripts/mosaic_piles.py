#!/usr/bin/env python

import argparse
import logging
import os
import json

from osgeo import gdal, gdal_array

    
def main():
    aparser = argparse.ArgumentParser(
        description='Run analysis on a set of unit field piles')

    aparser.add_argument('dir', default='.',
                         help='Directory containing a set of unit field piles.')
    
    args = aparser.parse_args()

    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    mosaic_filename = os.path.join(args.dir,'mosaic.tif')
    mosaic_ds = gdal.GetDriverByName('GTiff').Create(
        mosaic_filename, 4096, 4096, 1, gdal.GDT_UInt16)

    file_list = os.listdir(args.dir)
    for filename in file_list:
        if (not filename.startswith('ufr_')) or (not filename.endswith('_metadata.json')):
            continue

        pile_name = '_'.join(filename.split('_')[1:3])

        file_path = os.path.join(args.dir, filename)

        pile_md = json.load(open(file_path))

        print pile_name

        sharpest_i = -1
        sharpest_value = 0

        for i in range(len(pile_md['sharpness'])):
            sharpness = pile_md['sharpness'][i]
            if sharpness > sharpest_value:
                sharpest_value = sharpness
                sharpest_i = i

        print sharpest_i, sharpest_value

        
        raw_filename = os.path.join(
            args.dir,
            'ufr_' + pile_name + '_datacube_raw.tif')

        raw = gdal_array.LoadFile(raw_filename)
        best_img = raw[sharpest_i]
        gdal_array.SaveArray(
            best_img, 
            os.path.join(
                args.dir,
                'ufr_' + pile_name + '_best.tif'))
        
        uf_i = int(pile_name.split('_')[0])
        uf_j = int(pile_name.split('_')[1])

        mosaic_ds.GetRasterBand(1).WriteArray(
            best_img, uf_i * 256, uf_j * 256)

    print 'See ', mosaic_filename

if __name__ == '__main__':
    main()
