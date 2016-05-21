import os
import logging
import numpy
import json

from osgeo import gdal, gdal_array

from ground_surveyor import gsconfig

UF_TILE_SIZE = gsconfig.UF_TILE_SIZE

def split_row_of_unit_fields(output_dir, metatiles, ytile):
    # Determine metatile size and bit depth.
    mt_ds = gdal.Open(metatiles[0])
    assert mt_ds.RasterXSize % UF_TILE_SIZE == 0
    assert mt_ds.RasterYSize % UF_TILE_SIZE == 0

    x_uf_count = mt_ds.RasterXSize / UF_TILE_SIZE
    y_uf_count = mt_ds.RasterYSize / UF_TILE_SIZE

    dt = mt_ds.GetRasterBand(1).DataType

    assert ytile >= 0 and ytile < y_uf_count

    piles = [[] for x in range(x_uf_count)]
    piles_md = [[] for x in range(x_uf_count)]

    for metatile in metatiles:

        mt_ds = gdal.Open(metatile)
        mt_basename = os.path.basename(metatile)

        assert mt_ds.RasterXSize == x_uf_count * UF_TILE_SIZE
        assert mt_ds.RasterYSize == y_uf_count * UF_TILE_SIZE

        # Collect the metadata.  For now this is hardcoded to PlanetScope
        # mosaic metatile naming.
        metatile_md = {}

        if os.path.exists(metatile+'.json'):
            core_name = mt_basename.split('.')[2]
            metatile_md['cpu_hostname'] = core_name.split('_')[2]
            metatile_md['timestamp'] = int(core_name.split('_')[0])*1000000.0 \
                                       + int(core_name.split('_')[1])
            metatile_md['filename'] = mt_basename

        work_band = mt_ds.GetRasterBand(1)
        alpha_band = mt_ds.GetRasterBand(4)
        
        for xtile in range(x_uf_count):
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

            piles[xtile].append(
                work_band.ReadAsArray(
                    xtile*UF_TILE_SIZE, ytile*UF_TILE_SIZE,
                    UF_TILE_SIZE, UF_TILE_SIZE))

            piles_md[xtile].append(metatile_md)

    # Now write all the piles.  They will have different numbers of bands
    # depending on how many good unit fields were available. 
    for xtile in range(x_uf_count):
        uf_name = os.path.join(
            output_dir,
            'uf_%02d_%02d_raw.tif' % (xtile, ytile))

        # TODO: it would be nice to preserve the georeferencing on the
        # unit fields!
        gdal_array.SaveArray(numpy.array(piles[xtile]), uf_name)
        
        json.dump(piles_md[xtile],
                  open(os.path.splitext(uf_name)[0] + '.json','w'),
                  indent=4)

def split_metatiles(output_dir, metatiles):

    # Determine metatile size and bit depth.
    mt_ds = gdal.Open(metatiles[0])
    assert mt_ds.RasterXSize % UF_TILE_SIZE == 0
    assert mt_ds.RasterYSize % UF_TILE_SIZE == 0

    x_uf_count = mt_ds.RasterXSize / UF_TILE_SIZE
    y_uf_count = mt_ds.RasterYSize / UF_TILE_SIZE

    for ytile in range(y_uf_count):
        print 'Process Row: ', ytile
        split_row_of_unit_fields(output_dir, metatiles, ytile)
        
    logging.info('Wrote %d piles to directory %s.',
                 x_uf_count * y_uf_count, output_dir)
