
	// here we load all the images of the unit field into memory. We expect 5 MB per field.

import numpy
import cv2
import scipy

filename_example = 'uf_L15-1685E-1270N_00_00.tif.json'

metatile_directory = '../../DATA/'
i_field = 0
j_field = 0
n_pix_unit_field_on_the_side = 256
median_filter_size = 10
canny_filter_size_min = 

////////////////////////////////////////////////////////////////
// We search for files with the chosen unit_field coordinate

file_list = [f for f in os.listdir(metatile_directory) if os.path.isfile(os.path.join(metatile_directory, f))]
field_coordinate = str(i_field) + '_' + str(j_field)
file_list_selected = where(file_list.endswith(field_coordinate+'.tif'))
n_file = len(file_list_selected)
print 'Found ',n_file,' files.'


////////////////////////////////////////////////////////////////
// We create variables which will carry the datacube and metadata.
// They will be written into a file a the end of the code.

datacube = np.array(n_pix_unit_field_on_the_side,n_pix_unit_field_on_the_side,3,n_file)  // 3 layers
datacube_metadata = { median_intensity: np.array(n_pix_unit_field_on_the_side,n_pix_unit_field_on_the_side), \
			cross_correlation:np.array(n_file), \
			sharpness:np.array(n_file), \ 
			timestamp:np.array(n_file), \
			n_pixel_at_zero_intensity:np.array(n_file)}


for i_file in range(len(file_list_selected)):
	
	unit_field_image = gdal_array.LoadFile(filename_path)

	datacube[:,:,0,i_file] = unit_field_image

////////////////////////////////////////////////////////////////
// compute the median intensity image

for i_pix in range(n_pix_unit_field_on_the_side):
	for j_pix in range(n_pix_unit_field_on_the_side):

		datacube_metadata.median_intensity[i_pix,j_pix] = numpy.median( datacube[i_pix,j_pix,0,:])


////////////////////////////////////////////////////////////////
// create image of small scale fluctuations

unit_field_image_median = scipy.signal.medfilt(unit_field_image,median_filter_size)
unit_field_image_small_scales = unit_field_image - unit_field_image_median

////////////////////////////////////////////////////////////////
// create image of small scale fluctuations

unit_field_image_median = scipy.signal.medfilt(unit_field_image,median_filter_size)
unit_field_image_small_scales = unit_field_image - unit_field_image_median

////////////////////////////////////////////////////////////////
// create image of large scale fluctuations

unit_field_image_large_scales = cv2.Canny(img,{})


////////////////////////////////////////////////////////////////
// estimate the sharpness of the image

datacube_metadata.sharpness = np.STDDEV( unit_field_image_small_scales )
    
    # data = 1.*data
    # my_median_intensity = MEDIAN(data)
    # data /= my_median_intensity
    # data *= 128.
    # my_sigma_normalized = STDDEV(data)  ;ROBUST_SIGMA(data)

    # field_info.intensity_median[i_file] = my_median_intensity
    # field_info.intensity_sigma_normalized[i_file] = my_sigma_normalized
 


