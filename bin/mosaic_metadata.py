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

    mosaic_filename = os.path.join(args.dir,'mosaic_test.tif')

    metadata_image = numpy.zeros( (16,16) )

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


        sharpest_i = -1
        sharpest_value = 0

        for i in range(len(pile_md['sharpness'])):
            sharpness = pile_md[args.measure][i]
            if sharpness > sharpest_value:
                sharpest_value = sharpness
                sharpest_i = i

#        print sharpest_i, sharpest_value

        uf_i = int(pile_name.split('_')[0])
        uf_j = int(pile_name.split('_')[1])
        metadata_image[uf_i,uf_j] = sharpest_value
        

#        mosaic_ds.GetRasterBand(1).WriteArray(
#            metadata_image, uf_i, uf_j)

    gdal_array.SaveArray(metadata_image, 'test.tif')

#     gdal_array.SaveArray(numpy.reshape(dc.median,
#                                        (3,n_pix_unit_field_on_the_side,
#                                         n_pix_unit_field_on_the_side)),
#                          basepath + '_medians.tif')



    print 'See ', mosaic_filename

if __name__ == '__main__':
    main()
