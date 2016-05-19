PRO DISPLAY_INFO,field_map,field_list,field_info,charsize=charsize,n_field_side,field_list_s,$
                 choice_image_type

n_pix_field = 4096 / n_field_side

my_min_corr = 0.6

n_file = field_map.n_file
print,'Number of files: ',n_file

number_of_panels_to_show = n_file
MULTIPLOT,fix(sqrt(number_of_panels_to_show)+1)*[1,1]
erase
loadct,0,/silent



;; -- display median image
field_list_histeq = field_list
for i_image=0,n_file-1 do begin
    field_list_histeq[*,*,i_image] = HIST_EQUAL(field_list[*,*,i_image])
endfor
image_median = MEDIAN(field_list_histeq,dimension=3)
DISPLAY_BM, image_median,tit='median'
MULTIPLOT


for i_image=0,n_file-1 do begin
    

    data = 1.*field_list[*,*,i_image]


    DISPLAY_BM,HIST_EQUAL(data),/noerase
;    DISPLAY_BM,(data),/noerase

    my_y_text = 10
    
    ;; -- display left correlation coefficients
    for i_corr=0,2 do begin

        if i_corr eq 0 then corr_value = field_info.corr_Spearman_rank[i_image]
        if i_corr eq 1 then corr_value = field_info.corr_Spearman_rank_s[i_image]
        if i_corr eq 2 then corr_value = field_info.corr_Spearman_rank_l[i_image]


        my_color=getcolor('orange',1)
        
        if corr_value gt my_min_corr then my_color=getcolor('green',2) 
    
        xyouts,10,my_y_text,string(format='(f7.2)',corr_value),$
          color=my_color,charsize=charsize
        my_y_text += 20
    endfor
    


    ;; -- display right, satellite, date, n_pix_bad
    my_y_text_right = 10
    my_x_text_right = n_pix_field-10
    my_color=getcolor('green',1)
    my_text = field_map.sat_ref[i_image]
    xyouts,my_x_text_right,my_y_text_right,my_text,charsize=charsize,align=1,$
      color=my_color

    my_y_text_right += 20
    my_text = string(format='(f8.2)',field_map.timestamp[i_image]-800)
    xyouts,my_x_text_right,my_y_text_right,my_text,charsize=charsize,align=1,$
      color=my_color

    my_y_text_right += 20
    my_text = field_info.n_pix_zero[i_image]
    xyouts,my_x_text_right,my_y_text_right,my_text,charsize=charsize,align=1,$
      color=my_color

    loadct,0,/silent




    ;; -- add histograms

    my_color=getcolor('green',1)
    my_y_text = 200
    my_x_text = 20

    xyouts,my_x_text,my_y_text,string(format='(f7.2)',field_info.intensity_median[i_image]),$
      color=my_color,charsize=charsize

    my_y_text -= 20
    xyouts,my_x_text,my_y_text,string(format='(f7.2)',field_info.intensity_sigma_normalized[i_image]),$
      color=my_color,charsize=charsize


    my_text = field_info.sigma_data_s[i_image]
    my_y_text -= 20
    xyouts,my_x_text,my_y_text,string(format='(f7.2)',my_text),$
      color=my_color,charsize=charsize

   
    data_for_histogram = 128. * data / field_info.intensity_median[i_image] 
    PLOTHIST,data_for_histogram,x_hist,y_hist,/noerase,color=getcolor('blue',1),xr=[0,1500]

    data_s_for_histogram = 1.*field_list_s[*,*,i_image] ;/ field_info.intensity_sigma_normalized[i_image]
    PLOTHIST,data_s_for_histogram,x_hist,y_hist,/noerase,color=getcolor('green',1),xr=[-200,200]
        
    loadct,0,/silent
    

    multiplot


    
endfor




END
