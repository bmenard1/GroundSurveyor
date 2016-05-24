# here we load all the images of the unit field into memory. We expect 5 MB per field.

import os
import numpy
import scipy
import scipy.ndimage
import scipy.signal
import json

from osgeo import gdal_array, gdal

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

def load_pile(pile_filename):
    dc = DataCube()
    
    ## -- This looks for files with "ufr_". It would be good to get rid of the extra "r" at some point.
    filename_only = pile_filename.split('/')[-1]
    filename_base = 'ufr' + filename_only.strip('raw.tif').strip('uf')
    path_only = os.path.dirname(pile_filename)
    pile_small_filename = path_only + '/' + filename_base +'small.tif'
    pile_large_filename = path_only + '/' + filename_base +'large.tif'
    
    raw_ds = gdal.Open(pile_filename)
    raw_small = gdal.Open(pile_small_filename)
    raw_large = gdal.Open(pile_large_filename)

    dc.input_metadata = json.load(
        open(os.path.splitext(pile_filename)[0]+'.json'))
    
    dc.n_file = raw_ds.RasterCount

    dc.cube = numpy.zeros((3,dc.n_file,  
                           gsconfig.UF_TILE_SIZE,
                           gsconfig.UF_TILE_SIZE))
    
    ## one median image for each layer (raw, small, large)
    dc.median = numpy.zeros( (3,gsconfig.UF_TILE_SIZE,gsconfig.UF_TILE_SIZE,) )
    
    dc.metadata = { 
        'cross_correlation_raw': numpy.zeros(dc.n_file),
	'cross_correlation_small': numpy.zeros(dc.n_file),
	'cross_correlation_large': numpy.zeros(dc.n_file),
	'sharpness': numpy.zeros(dc.n_file), 
	'timestamp': numpy.zeros(dc.n_file), 
	'n_pixel_at_zero_intensity': numpy.zeros(dc.n_file)}
    
    for i_file in range(dc.n_file):
        
        ## BM: why +1 needed?
        dc.cube[0,i_file,:,:] = raw_ds.GetRasterBand(i_file+1).ReadAsArray()
        dc.cube[1,i_file,:,:] = raw_small.GetRasterBand(i_file+1).ReadAsArray()
        dc.cube[2,i_file,:,:] = raw_large.GetRasterBand(i_file+1).ReadAsArray()
        
	dc.metadata['timestamp'][i_file] \
            = dc.input_metadata[i_file]['timestamp']

    return dc
    
    
def compute_median(dc):
        
    ## Now that all the unit fields are loaded in memory, we can compute 
    ##  the median intensity image
#    for i_pix in range(n_pix_unit_field_on_the_side):
#        for j_pix in range(n_pix_unit_field_on_the_side):
    for i_layer in range(3):
        dc.median[i_layer] = numpy.median( dc.cube[i_layer,:,:,:],axis=0)



def analyse_pile(dc):
    for i_file in range(dc.n_file):

        unit_field_image = dc.cube[0,i_file,:,:]
        unit_field_image_small_scales = dc.cube[1,i_file,:,:]

	## estimate the sharpness of the image
	dc.metadata['sharpness'][i_file] = numpy.std( unit_field_image_small_scales )

	## estimate the number of pixels with I=0
	dc.metadata['n_pixel_at_zero_intensity'][i_file] = \
            (unit_field_image.shape[0] * unit_field_image.shape[1]) - numpy.count_nonzero(unit_field_image) 




def compute_spatial_cross_correlations(dc):

    #////////////////////////////////////////////////////////////////
    ## Spatial cross-correlations with respect to the median image

    for i_layer in range(3):

#        Y = dc.cube[i_layer][-1][:,:]
        Y = dc.median[i_layer][:,:]

        if i_layer == 0:
            my_key = 'cross_correlation_raw'
        if i_layer == 1:
            my_key = 'cross_correlation_small'
        if i_layer == 2:
            my_key = 'cross_correlation_large'

        for i_file in range(dc.n_file):

            X = dc.cube[i_layer][i_file][:,:]
            dc.metadata[my_key][i_file] = scipy.stats.spearmanr(X,Y,axis=None)[0]




def save_statistics(dc, basepath=''):
    for key in dc.metadata.keys():
	try:
            dc.metadata[key] = list(dc.metadata[key])
	except:
            pass

    json.dump(dc.metadata,
              open(basepath+'_datacube_metadata.json','w'),
              indent=4)

    gdal_array.SaveArray(numpy.reshape(dc.median,
                                       (3,n_pix_unit_field_on_the_side,
                                        n_pix_unit_field_on_the_side)),
                         basepath + '_medians.tif')



if __name__ == '__main__':

    metatile_directory = 'data/beijing_uf'
    i_field = 15
    j_field = 15

    ##  We search for files with the chosen unit_field coordinate

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
    save_statistics(dc)

