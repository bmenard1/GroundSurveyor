# here we load all the images of the unit field into memory. We expect 5 MB per field.

import os
import numpy
import cv2
import scipy
import scipy.signal
import json
from osgeo import gdal_array

metatile_directory = 'data/beijing_uf'
i_field = 15
j_field = 15

n_pix_unit_field_on_the_side = 256  # expected
median_filter_size = 11
canny_filter_size_min = 6
canny_filter_size_max = 20


#////////////////////////////////////////////////////////////////
#// We search for files with the chosen unit_field coordinate

file_list = [f for f in os.listdir(metatile_directory) if os.path.isfile(os.path.join(metatile_directory, f))]
field_coordinate = 'uf_%02d_%02d_' % (i_field, j_field)

def our_coord(item):
	return item.startswith(field_coordinate) and item.endswith('.tif')

file_list_selected = [os.path.join(metatile_directory,name) \
			      for name in filter(our_coord,file_list)]
n_file = len(file_list_selected)
print 'Found ',n_file,' files.'


#////////////////////////////////////////////////////////////////
#// We create variables which will carry the datacube and metadata.
#// They will be written into a file a the end of the code.

## The order of the indices allows us later to create a convenient format 
## to display the pile of unit_field images
datacube = numpy.zeros((3,n_file+1,  
			n_pix_unit_field_on_the_side,
			n_pix_unit_field_on_the_side))  # 3 layers

datacube_metadata = { 
	'cross_correlation': numpy.zeros(n_file),
	'sharpness': numpy.zeros(n_file), 
	'timestamp': numpy.zeros(n_file), 
	'n_pixel_at_zero_intensity': numpy.zeros(n_file),
	}

for i_file in range(len(file_list_selected)):
	
	unit_field_filename_path = file_list_selected[i_file]
	unit_field_image = gdal_array.LoadFile(unit_field_filename_path)

	unit_field_metadata_filename_path = unit_field_filename_path + '.json'
	unit_field_metadata = json.loads(unit_field_metadata_filename_path



    #////////////////////////////////////////////////////////////////
    #// load a one band image for the selected unit field
	datacube[0,i_file,:,:] = unit_field_image

    #////////////////////////////////////////////////////////////////
    #// create image of small scale fluctuations
	unit_field_image_median = scipy.signal.medfilt(unit_field_image,median_filter_size)
	unit_field_image_small_scales = unit_field_image - unit_field_image_median
	datacube[1,i_file,:,:] = unit_field_image_small_scales


	#////////////////////////////////////////////////////////////////
	#// create image of large scale fluctuations
	unit_field_image_large_scales = cv2.Canny(img,canny_filter_size_min,canny_filter_size_max)


	#////////////////////////////////////////////////////////////////
	#// estimate the sharpness of the image
	datacube_metadata['sharpness'][i_file] = numpy.std( unit_field_image_small_scales )


	#////////////////////////////////////////////////////////////////
	#// estimate the number of pixels with I=0
	datacube_metadata['n_pixel_at_zero_intensity'][i_file] = /
		sum(intensity_value == 0 for intensity_value in unit_field_image)

	#////////////////////////////////////////////////////////////////
	#// get the timestamp
	datacube_metadata['timestamp'][i_file] = unit_field_metadata.timestamp



#////////////////////////////////////////////////////////////////
## Now that all the unit fields are loaded in memory, we can compute 
##  the median intensity image
for i_pix in range(n_pix_unit_field_on_the_side):
	for j_pix in range(n_pix_unit_field_on_the_side):

		datacube[0][-1][i_pix,j_pix] = \
		    numpy.median( datacube[0,:,i_pix,j_pix])
		datacube[1][-1][i_pix,j_pix] = \
		    numpy.median( datacube[1,:,i_pix,j_pix])
		datacube[2][-1][i_pix,j_pix] = \
		    numpy.median( datacube[2,:,i_pix,j_pix])


   
    # data = 1.*data
    # my_median_intensity = MEDIAN(data)
    # data /= my_median_intensity
    # data *= 128.
    # my_sigma_normalized = STDDEV(data)  ;ROBUST_SIGMA(data)

    # field_info.intensity_median[i_file] = my_median_intensity
    # field_info.intensity_sigma_normalized[i_file] = my_sigma_normalized

for key in datacube_metadata.keys():
	try:
		datacube_metadata[key] = list(datacube_metadata[key])
	except:
		pass

json.dump(datacube_metadata,open('datacube_metadata.json','w'),
	  indent=4)

gdal_array.SaveArray(
	numpy.reshape(datacube[0,:,:,:],
		      (n_file+1,
		       n_pix_unit_field_on_the_side,
		       n_pix_unit_field_on_the_side)),
	'datacube_raw.tif')
gdal_array.SaveArray(
	numpy.reshape(datacube[1,:,:,:],
		      (n_file+1,
		       n_pix_unit_field_on_the_side,
		       n_pix_unit_field_on_the_side)),
	'datacube_small.tif')
gdal_array.SaveArray(
	numpy.reshape(datacube[2,:,:,:],
		      (n_file+1,
		       n_pix_unit_field_on_the_side,
		       n_pix_unit_field_on_the_side)),
	'datacube_large.tif')
