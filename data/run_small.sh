#!/bin/bash

mkdir -p small_uf
make_piles_of_unit_fields.py -o small_uf \
    beijing_metatiles/L15-1685E-1270N.0.20140713_021839_0903.tif.mq.tif \
    beijing_metatiles/L15-1685E-1270N.0.20140713_021840_0903.tif.mq.tif

compute_pile_statistics.py small_uf/*_raw.tif
mosaic_piles.py small_uf

metatile_stats.py --stat variance small_uf


