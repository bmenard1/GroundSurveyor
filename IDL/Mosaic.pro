my_choice = 0


my_n_field_side = 16
date_list = fltarr(my_n_field_side^2)
i_field_tot = 0L
for j_field = 0,my_n_field_side-1 do begin
    for i_field = 0,my_n_field_side-1 do begin
        
;        field_info = metatile_info[i_field,j_field]
        field_map = map[i_field,j_field]
        n_file = field_map.n_file
        
        id_image = where( field_map.timestamp[0:n_file-1] eq max(field_map.timestamp[0:n_file-1]),count)
        date_list[i_field_tot] = field_map.timestamp[id_image(0)]
        i_field_tot++
    endfor
endfor

ERASE
MULTIPLOT,[my_n_field_side,my_n_field_side]

n_pix_per_field = 256
large_image = intarr(my_n_field_side*n_pix_per_field , my_n_field_side*n_pix_per_field)

for j_field = 0,my_n_field_side-1 do begin
    for i_field = 0,my_n_field_side-1 do begin
        
        field_map = map[i_field,j_field]
        n_file = field_map.n_file

        field_info = metatile_info[i_field,j_field]

        image_list = metatile_image[i_field,j_field].raw[*,*,0:n_file-1]
        
        ;; -- good mosaic
        if my_choice eq 0 then begin
            ;; -- remove images with bad pixels
            id_ok = where( (field_info.n_pix_zero eq 0) AND $
                           (field_map.timestamp gt 1200) AND $
                           (fix(field_map.timestamp) ne 1467) And $
                           (field_info.corr_Spearman_rank gt 0.5) )
            
            ;; -- sharp
            id_sharp = REVERSE(SORT(field_info.sigma_data_s[id_ok]))
            
            id_image_to_display = id_ok[id_sharp[0]]
        endif


        ;; -- latest image
        if my_choice eq 1 then begin
            id_ok = REVERSE(SORT(field_map.timestamp))
            id_image_to_display = id_ok[0]
        endif

        ;; -- odlder image
        if my_choice eq 2 then begin
            id_ok = where( field_map.timestamp le 1300 )
            id_select = REVERSE(SORT(field_map.timestamp[id_ok]))
            id_image_to_display = id_ok[id_select[0]]
        endif

        

        image_to_display = 1.*image_list[*,*, id_image_to_display ]
        DISPLAY_BM,HIST_EQUAL(image_to_display),/noerase,color=getcolor('black',1)

        my_text = string(format='(i4)',field_map.timestamp[id_image_to_display])
        xyouts,10,10,my_text,color=getcolor('green',1),charsize=1,charthick=0.5

        if (j_field eq 0) then begin
            my_tit=string(format="(i2)",i_field)
            xyouts,0,260,my_tit,align=0.
        endif
        if (i_field eq 0) then begin
            my_tit=string(format="(i2)",j_field)
            xyouts,-50,100,my_tit,align=1.
        endif



        loadct,0,/silent

        MULTIPLOT
        
        id_pix_x = i_field*n_pix_per_field + indgen(n_pix_per_field)
        id_pix_y = j_field*n_pix_per_field + indgen(n_pix_per_field)

;        my_field_to_consider = HIST_EQUAL(field_to_display[*,*])

        large_image[i_field*n_pix_per_field:(i_field+1)*n_pix_per_field-1,$
                    (my_n_field_side-j_field-1)*n_pix_per_field:(my_n_field_side-j_field)*n_pix_per_field-1] = $
          1.d0*image_to_display / MEDIAN(1.*image_to_display) * 128

    endfor
endfor

MULTIPLOT,/DEFAULT
pause

;my_range = 256*8*[1,1]
DISPLAY_BM,(large_image),/noerase,color=getcolor('black',0);,xr=my_range,yr=my_range
pause

DISPLAY_BM,HIST_EQUAL(large_image),/noerase,color=getcolor('black',0);,xr=my_range,yr=my_range


end
