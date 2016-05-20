# here we load all the images of the unit field into memory. We expect 5 MB per field.

import os
import numpy
import cv2
import scipy
import scipy.ndimage
import scipy.signal
import json

from osgeo import gdal_array

from ground_surveyor import gsconfig

n_pix_unit_field_on_the_side = 256  # expected
median_filter_size = 11
canny_filter_size_min = 6
canny_filter_size_max = 20


class DataCube:
    def __init__(self):
        self.n_file = 0
        self.cube = None
        self.metadata = {}
        self.input_metadata = []

def load_pile(file_list_selected):
    dc = DataCube()

    dc.n_file = len(file_list_selected)

    dc.cube = numpy.zeros((3,dc.n_file+1,  
                           gsconfig.UF_TILE_SIZE,
                           gsconfig.UF_TILE_SIZE))  # 3 layers

    dc.metadata = { 
	'cross_correlation_raw': numpy.zeros(dc.n_file),
	'cross_correlation_small': numpy.zeros(dc.n_file),
	'cross_correlation_large': numpy.zeros(dc.n_file),
	'sharpness': numpy.zeros(dc.n_file), 
	'timestamp': numpy.zeros(dc.n_file), 
	'n_pixel_at_zero_intensity': numpy.zeros(dc.n_file),
	}

    for i_file in range(dc.n_file):

        unit_field_filename_path = file_list_selected[i_file]
	unit_field_image = gdal_array.LoadFile(unit_field_filename_path)

	unit_field_metadata_filename_path = os.path.splitext(unit_field_filename_path)[0] + '.json'

        json_data = open(unit_field_metadata_filename_path)

	unit_field_metadata = json.loads(json_data.read())

        #////////////////////////////////////////////////////////////////
        #// load a one band image for the selected unit field
        dc.cube[0,i_file,:,:] = unit_field_image
        dc.input_metadata.append(unit_field_metadata)
        
	#////////////////////////////////////////////////////////////////
	#// get the timestamp
	dc.metadata['timestamp'][i_file] = unit_field_metadata['timestamp']

    return dc

def analyse_pile(dc):
    for i_file in range(dc.n_file):

        print i_file,dc.n_file
        
	unit_field_image = dc.cube[0,i_file,:,:]
        
        #////////////////////////////////////////////////////////////////
        #// create image of small scale fluctuations
	unit_field_image_median = scipy.signal.medfilt(unit_field_image,median_filter_size)
	unit_field_image_small_scales = unit_field_image - unit_field_image_median
	dc.cube[1,i_file,:,:] = unit_field_image_small_scales


	#////////////////////////////////////////////////////////////////
	#// create image of large scale fluctuations
        I_large_min = scipy.ndimage.filters.gaussian_filter(unit_field_image, 6)
        I_large_max = scipy.ndimage.filters.gaussian_filter(unit_field_image, 20)

        unit_field_image_large_scales = I_large_min - I_large_max
        dc.cube[2,i_file,:,:] = unit_field_image_large_scales

	#////////////////////////////////////////////////////////////////
	#// estimate the sharpness of the image
	dc.metadata['sharpness'][i_file] = numpy.std( unit_field_image_small_scales )


	#////////////////////////////////////////////////////////////////
	#// estimate the number of pixels with I=0
	dc.metadata['n_pixel_at_zero_intensity'][i_file] = \
            (unit_field_image.shape[0] * unit_field_image.shape[1]) - numpy.count_nonzero(unit_field_image) 


def compute_median(dc):

    #////////////////////////////////////////////////////////////////
    ## Now that all the unit fields are loaded in memory, we can compute 
    ##  the median intensity image
    for i_pix in range(n_pix_unit_field_on_the_side):
	for j_pix in range(n_pix_unit_field_on_the_side):
            
            dc.cube[0][-1][i_pix,j_pix] = \
                numpy.median( dc.cube[0,:,i_pix,j_pix])
            dc.cube[1][-1][i_pix,j_pix] = \
                numpy.median( dc.cube[1,:,i_pix,j_pix])
            dc.cube[2][-1][i_pix,j_pix] = \
                numpy.median( dc.cube[2,:,i_pix,j_pix])


   
    # data = 1.*data
    # my_median_intensity = MEDIAN(data)
    # data /= my_median_intensity
    # data *= 128.
    # my_sigma_normalized = STDDEV(data)  ;ROBUST_SIGMA(data)

    # field_info.intensity_median[i_file] = my_median_intensity
    # field_info.intensity_sigma_normalized[i_file] = my_sigma_normalized


def compute_spatial_cross_correlations(dc):

    #////////////////////////////////////////////////////////////////
    ## Spatial cross-correlations with respect to the median image

    for i_layer in range(3):

        print i_layer,' / ',2

        Y = dc.cube[i_layer][-1][:,:]

        if i_layer == 0:
            my_key = 'cross_correlation_raw'
        if i_layer == 1:
            my_key = 'cross_correlation_small'
        if i_layer == 2:
            my_key = 'cross_correlation_large'

        for i_file in range(dc.n_file):

            X = dc.cube[i_layer][i_file][:,:]
            print numpy.median(X),numpy.median(Y)
            print my_key,'=',scipy.stats.spearmanr(X,Y,axis=None)[0]
            dc.metadata[my_key][i_file] = scipy.stats.spearmanr(X,Y,axis=None)[0]




def save_pile(dc, basepath=''):
    for key in dc.metadata.keys():
	try:
            dc.metadata[key] = list(dc.metadata[key])
	except:
            pass

    json.dump(dc.metadata,
              open(basepath+'datacube_metadata.json','w'),
              indent=4)

    gdal_array.SaveArray(
	numpy.reshape(dc.cube[0,:,:,:],
		      (dc.n_file+1,
		       n_pix_unit_field_on_the_side,
		       n_pix_unit_field_on_the_side)),
	basepath+'datacube_raw.tif')
    gdal_array.SaveArray(
	numpy.reshape(dc.cube[1,:,:,:],
		      (dc.n_file+1,
		       n_pix_unit_field_on_the_side,
		       n_pix_unit_field_on_the_side)),
	basepath+'datacube_small.tif')
    gdal_array.SaveArray(
	numpy.reshape(dc.cube[2,:,:,:],
		      (dc.n_file+1,
		       n_pix_unit_field_on_the_side,
		       n_pix_unit_field_on_the_side)),
	basepath+'datacube_large.tif')


if __name__ == '__main__':

    metatile_directory = 'data/beijing_uf'
    i_field = 15
    j_field = 15

    #////////////////////////////////////////////////////////////////
    #// We search for files with the chosen unit_field coordinate

    file_list = [f for f in os.listdir(metatile_directory) if os.path.isfile(os.path.join(metatile_directory, f))]
    field_coordinate = 'uf_%02d_%02d_' % (i_field, j_field)

    def our_coord(item):
	return item.startswith(field_coordinate) and item.endswith('.tif')

    file_list_selected = [os.path.join(metatile_directory,name) \
			      for name in filter(our_coord,file_list)]

    file_list_selected = file_list_selected[0:4]

    n_file = len(file_list_selected)
    print 'Found ',n_file,' files.'


    dc = load_pile(file_list_selected)
    print 'analyse...'
    analyse_pile(dc)
    print 'median images...'
    compute_median(dc)
    print 'spatial cross-correlations...'
    compute_spatial_cross_correlations(dc)
    print 'save...'
    save_pile(dc)

    


        #img_8bit = (unit_field_image/16).astype(numpy.uint8)
        #cv_img = cv2.cvtColor(img_8bit, cv2.COLOR_GRAY2GRAY)
	#unit_field_image_large_scales = cv2.Canny(unit_field_image,
        #                                          canny_filter_size_min,canny_filter_size_max)
