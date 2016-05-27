import os
import json
import logging

from osgeo import gdal

from ground_surveyor import gsconfig


def pick_best_pile_layer(pile_md_filename,
                         selection_options):

    pile_md = json.load(open(pile_md_filename))
        
    best_i = -1
    best_value = 0

    target_field = selection_options.get('order_field',
                                         'normalized_sharpness')
    cc_threshold = selection_options.get('cross_correlation_threshold',
                                         None)
    
    for i in range(len(pile_md['sharpness'])):
        if cc_threshold is not None:
            cc_raw = pile_md['cross_correlation_raw'][i]
            if cc_raw < cc_threshold:
                continue

        if target_field == 'normalized_sharpness':
            target_value = pile_md['sharpness'][i] \
                / pile_md['intensity_median'][i]
        else:
            target_value = pile_md[target_field]

        if target_value > best_value:
            best_value = target_value
            best_i = i

    # If nothing met the threshold, try again without the threshold.
    if best_i == -1 and cc_threshold is not None:
        for i in range(len(pile_md['sharpness'])):
            if target_field == 'normalized_sharpness':
                target_value = pile_md['sharpness'][i] \
                    / pile_md['intensity_median'][i]
            else:
                target_value = pile_md[target_field]

            if target_value > best_value:
                best_value = target_value
                best_i = i

    logging.debug('Picked input metatile %d for pile %s with %s value of %s.',
                  best_i,
                  os.path.basename(pile_md_filename)[:15],
                  target_field, best_value)

    return best_i


def get_pile_layer(pile_md_filename, i_file):
    raw_filename = pile_md_filename.replace('_datacube_metadata.json',
                                            '_raw.tif')
    raw_ds = gdal.Open(raw_filename)
    return raw_ds.GetRasterBand(i_file+1).ReadAsArray()


def merge_pile_into_mosaic(mosaic_ds, 
                           pile_md_filename,
                           selected_i,
                           selected_img,
                           processing_options):

    pile_parts = os.path.basename(pile_md_filename).split('_')[0:3]
    assert pile_parts[0] == 'uf'

    uf_i = int(pile_parts[1])
    uf_j = int(pile_parts[2])

    if processing_options.get('normalize_intensity',False):
        pile_md = json.load(open(pile_md_filename))
        selected_img = selected_img * 1000.0 \
            / pile_md['intensity_median'][selected_i]


    mosaic_ds.GetRasterBand(1).WriteArray(
        selected_img, uf_i * 256, uf_j * 256)


def make_metatile(pile_directory):
    mosaic_filename = os.path.join(pile_directory,'mosaic.tif')
    mosaic_ds = gdal.GetDriverByName('GTiff').Create(
        mosaic_filename, 4096, 4096, 1, gdal.GDT_UInt16)

    # TODO: Try to add georeferencing...

    return mosaic_filename, mosaic_ds


def mosaic_metatile(pile_directory,
                    selection_options, 
                    processing_options={}):

    mosaic_filename, mosaic_ds = make_metatile(pile_directory)

    counter = 0
    for filename in os.listdir(pile_directory):
        if (not filename.startswith('uf_')) or (not filename.endswith('_metadata.json')):
            continue

        pile_md_filename = os.path.join(pile_directory, filename)
        
        i_file = pick_best_pile_layer(pile_md_filename, selection_options)
        if i_file >= 0:
            selected_img = get_pile_layer(pile_md_filename, i_file)
            merge_pile_into_mosaic(mosaic_ds, pile_md_filename, 
                                   i_file, selected_img,
                                   processing_options)
            counter += 1

    logging.info('%d piles contributed to making %s.',
                 counter, mosaic_filename)

    return mosaic_filename

