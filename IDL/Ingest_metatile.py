# %matplotlib inline
import warnings
import matplotlib.pyplot as plt
import numpy as np
import scipy
import os
from osgeo import gdal_array,gdal
import pyfits
import sys


print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)

if len(sys.argv) < 2:
    print 'code expecting area_name, x and y tile numbers'

area = str(sys.argv[1])    
user_x_tile_number = sys.argv[2]
user_y_tile_number = sys.argv[3]

print area
print user_y_tile_number,user_y_tile_number

# if str(sys.argv) == 'Alberta':
#     area = 'Alberta'
#     my_x_min = ['0403', '0404', '0405']
#     my_y_min = ['1368', '1369']
# if str(sys.argv) == 'Beijing':
#     area = 'Beijing'
#     my_x_min = ['1685', '1686', '1687']
#     my_y_min = ['1270', '1271']
# if str(sys.argv) == 'Dubai':
#     area = 'Dubai'
#     my_x_min = ['1337', '1338', '1339']
#     my_y_min = ['1170','1171', '1172']


path_data = '/scratch/gwln2/menard/DATA/Planet/'
path_TIFF = path_data + area + '/raw_TIFF/'
path_metatile = path_data + area + '/' + user_x_tile_number + '-' + user_y_tile_number + '/'
path_metatile_FITS = path_metatile + '/FITS/'

if not os.path.exists(path_metatile):
    os.makedirs(path_metatile)
if not os.path.exists(path_metatile_FITS):
    os.makedirs(path_metatile_FITS)



# ==================================================
print 'Converting TIFF -> FITS...'


file_list = [f for f in os.listdir(path_TIFF) if os.path.isfile(os.path.join(path_TIFF, f))]
# XXXX LIMIT XXXXX
#file_list = file_list[0:10]
print 'Found ',len(file_list),' files.'

#my_x_min_array = np.array(my_x_min)
#my_y_min_array = np.array(my_y_min)
    
for i_file in range(len(file_list)):


    file_found = file_list[i_file]
    print '-- file found: ',file_found


    ## Rename file if the format found is the one from Amazon S3
    if file_found.find('content-disposition') > 0:
        filename = file_found.split()[1].split('"')[1]
        print '   renaming S3 name > .tiff'#,filename
        os.rename(path_TIFF+file_found, path_TIFF+filename)
    else:
        filename = file_found


    filename_path = path_TIFF + filename
    if filename.endswith('.tif'):

        x_tile_number = ( filename.split('-')[1][0:4] )
        y_tile_number = ( filename.split('-')[2][0:4] )
        
        if (x_tile_number == user_x_tile_number) and (y_tile_number == user_y_tile_number):

            print '-- opening file '#,filename_path

            #    try:
            image = gdal_array.LoadFile(filename_path)

            filename_fits = path_metatile_FITS + filename + '.fit'
    
            print 'create fits file '+filename_fits+'...'
            #        with warnings.catch_warnings():
            #            warnings.simplefilter('ignore')
            hdu0 = pyfits.PrimaryHDU(image[:,:,:])
            hdu0.writeto(filename_fits,clobber=True)


#    except:
#        print '>> problem with file:',filename
#        pass


print 'reached the end.'
