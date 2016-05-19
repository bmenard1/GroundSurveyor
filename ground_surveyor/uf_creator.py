import os
import logging
import numpy
import json

from osgeo import gdal, gdal_array

UF_TILE_SIZE = 256

def split_metatile(output_dir, metatile):
    
    mt_basename = os.path.basename(metatile)
    mt_ds = gdal.Open(metatile)

    # Collect the metadata.  For now this is hardcoded to PlanetScope
    # mosaic metatile naming.
    metatile_md = {}

    if os.path.exists(metatile+'.json'):
        core_name = mt_basename.split('.')[2]
        metatile_md['cpu_hostname'] = core_name.split('_')[2]
        metatile_md['timestamp'] = int(core_name.split('_')[0]) * 1000000.0 \
            + int(core_name.split('_')[1])

    work_band = mt_ds.GetRasterBand(1)
    alpha_band = mt_ds.GetRasterBand(4)
    
    assert mt_ds.RasterXSize % UF_TILE_SIZE == 0
    assert mt_ds.RasterYSize % UF_TILE_SIZE == 0

    uf_count = 0
    for ytile in range(0,mt_ds.RasterYSize/256):
        for xtile in range(0,mt_ds.RasterXSize/256):
            uf_alpha = alpha_band.ReadAsArray(
                xtile*UF_TILE_SIZE, ytile*UF_TILE_SIZE,
                UF_TILE_SIZE, UF_TILE_SIZE)

            # we want to skip unit fields where we don't have all the pixels.
            total_pixels = UF_TILE_SIZE * UF_TILE_SIZE
            missing_pixels = total_pixels - numpy.count_nonzero(uf_alpha)
            missing_ratio = missing_pixels / float(total_pixels)

            if missing_ratio > 0:
                logging.debug('Skip tile %dx%d of %s, missing %d pixels.',
                              xtile, ytile, metatile, missing_pixels)
                continue

            uf_data = work_band.ReadAsArray(
                xtile*UF_TILE_SIZE, ytile*UF_TILE_SIZE,
                UF_TILE_SIZE, UF_TILE_SIZE)

            
            uf_name = os.path.join(
                output_dir,
                ('uf_%02d_%02d_' + os.path.splitext(mt_basename)[0] + '.tif') % (
                    xtile, ytile))

            # TODO: it would be nice to preserve the georeferencing on the
            # unit fields!
            gdal_array.SaveArray(uf_data, uf_name)

            json.dump(metatile_md,
                      open(os.path.splitext(uf_name)[0] + '.json','w'),
                      indent=4)
            uf_count += 1


    logging.info('Write %d unit fields from file %s.', 
                 uf_count, metatile)

    
