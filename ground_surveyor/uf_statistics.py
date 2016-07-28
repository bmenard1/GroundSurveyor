import os
import json
import logging
import numpy

from osgeo import gdal

from ground_surveyor import gsconfig


def compute_variance(pile_md_filename, processing_options):
    filename = pile_md_filename.replace('_datacube_metadata.json',
                                            '_raw_small.tif')
    small_stack = gdal.Open(filename).ReadAsArray()
    if len(small_stack.shape) == 2:
        small_stack = numpy.reshape(
            small_stack, 
            (1, small_stack.shape[0], small_stack.shape[1]))

    if small_stack.shape[0] <= 1:
        return numpy.zeros(small_stack.shape[1:])
    else:
        return numpy.var(small_stack, 0)
    
    
def merge_pile_into_metatile(metatile_ds, 
                             pile_md_filename,
                             stat_uf,
                             processing_options):

    pile_parts = os.path.basename(pile_md_filename).split('_')[0:3]
    assert pile_parts[0] == 'uf'

    uf_i = int(pile_parts[1])
    uf_j = int(pile_parts[2])

    metatile_ds.GetRasterBand(1).WriteArray(
        stat_uf, uf_i * 256, uf_j * 256)


def make_metatile(pile_directory, desired_value):
    metatile_filename = os.path.join(pile_directory,
                                     desired_value + '.tif')
    metatile_ds = gdal.GetDriverByName('GTiff').Create(
        metatile_filename, 4096, 4096, 1, gdal.GDT_Float32)

    # TODO: Try to add georeferencing...

    return metatile_filename, metatile_ds


def statistics_metatile(pile_directory,
                        desired_value,
                        processing_options={}):

    metatile_filename, metatile_ds = make_metatile(pile_directory,
                                                   desired_value)

    counter = 0
    for filename in os.listdir(pile_directory):
        if (not filename.startswith('uf_')) or (not filename.endswith('_metadata.json')):
            continue

        pile_md_filename = os.path.join(pile_directory, filename)
        
        if desired_value == 'variance':
            stat_uf = compute_variance(pile_md_filename, processing_options)

        merge_pile_into_metatile(metatile_ds, pile_md_filename, 
                                 stat_uf, processing_options)
        counter += 1

    logging.info('%d piles contributed to making %s.',
                 counter, metatile_filename)

    return metatile_filename

