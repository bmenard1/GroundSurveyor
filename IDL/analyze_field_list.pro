PRO ANALYZE_FIELD_LIST,field_map,field_list,field_info,field_list_extra

filter_n_pix = 10

n_file = field_map.n_file
print,'Number of files: ',n_file

n_pix_field = (size(field_list[*,*,0]))(1)

field_list_extra = fltarr(n_pix_field,n_pix_field,n_file,2)


;; ---------------------------------------------
;; -- define the median images
field_list_histeq = field_list
for i_image=0,n_file-1 do begin
    field_list_histeq[*,*,i_image] = HIST_EQUAL(field_list[*,*,i_image])
endfor

image_median = MEDIAN(field_list_histeq,dimension=3)


;image_median = (MEDIAN(field_list_histeq,dimension=3))
image_median_small_scale = (image_median) - MEDIAN(image_median,filter_n_pix)

image_median_edgedog = EDGE_DOG(image_median, RADIUS1=6.0, RADIUS2=20.0, THRESHOLD=my_threshold,$
                                ZERO_CROSSINGS=[0,255])

;; ---------------------------------------------


;; -- calculate all the summary statistics we will use later
;;    to assess the quality of the images

n_pix_zero_list = intarr(n_file)
for i_file=0,n_file-1 do begin
    

;    COUNTER,i_file,n_file-1
    data = field_list[*,*,i_file]
    
    
    id_pix_zero = WHERE(data eq 0,n_pix_zero)
    field_info.n_pix_zero[i_file] = n_pix_zero
    
    
    ;; -- main image field
    corr_Pearson_linear = CORRELATE(data,image_median)
    corr_Spearman_rank = R_CORRELATE(data,image_median)
    
    field_info.corr_Pearson_linear[i_file] = corr_Pearson_linear
    field_info.corr_Spearman_rank[i_file] = (corr_Spearman_rank)(0)
    
    
    ;; -- small scale
    data_small_scale = data - MEDIAN(data,filter_n_pix)
    
    field_info.corr_Pearson_linear_s[i_file] = CORRELATE(data,image_median)
    field_info.corr_Spearman_rank_s[i_file] = (R_CORRELATE(data_small_scale,image_median_small_scale))(0)


    ;; -- large scales
;    data_smoothed = SMOOTH(data, 5)
;    DATA_S = SOBEL( DATA )
            
    image_edgedog = EDGE_DOG(data, RADIUS1=6.0, RADIUS2=20.0, THRESHOLD=my_threshold,$
                             ZERO_CROSSINGS=[0,255])


    field_info.corr_Pearson_linear_l[i_file] = CORRELATE(image_edgedog,image_median_edgedog)
    field_info.corr_Spearman_rank_l[i_file] = (R_CORRELATE(image_edgedog,image_median_edgedog))(0)

    field_list_extra[*,*,i_file,0] = data_small_scale
    field_list_extra[*,*,i_file,1] = image_edgedog


    ;; -- sharpness
    my_sigma_s = STDDEV( ABS(data_small_scale) )
    field_info.sigma_data_s[i_file] = my_sigma_s

    data = 1.*data
    my_median_intensity = MEDIAN(data)
    data /= my_median_intensity
    data *= 128.
    my_sigma_normalized = STDDEV(data)  ;ROBUST_SIGMA(data)

    field_info.intensity_median[i_file] = my_median_intensity
    field_info.intensity_sigma_normalized[i_file] = my_sigma_normalized
    
    
    
endfor





end


