
RESOLVE_ROUTINE,'display_info'
RESOLVE_ROUTINE,'analyze_field_list'

filename_datacube = 'metatile_info_image_map_test.idl'

print,PATH_METATILE_IDL

user_choice = 0
print,'[1] Compute  '
print,'[2] Restore'
print,'[0] Display'
read,user_choice

n_file_max = max(map.n_file)
n_field_side = (size(map))(1)
n_pix_field = 4096 / n_field_side
print,'N_field_side=',n_field_side


if user_choice eq 1 then begin
    print,'==================================================='
    print,'  COMPUTE...'


    field_info_blank = {n_file:0,$
                        n_pix_zero:lonarr(n_file_max),$
                        corr_Pearson_linear:fltarr(n_file_max),$
                        corr_Spearman_rank:fltarr(n_file_max),$
                        corr_Pearson_linear_l:fltarr(n_file_max),$
                        corr_Spearman_rank_l:fltarr(n_file_max),$
                        corr_Pearson_linear_s:fltarr(n_file_max),$
                        corr_Spearman_rank_s:fltarr(n_file_max),$
                        sigma_data_s:fltarr(n_file_max),$
                        intensity_median:fltarr(n_file_max),$
                        intensity_sigma_normalized:fltarr(n_file_max)}
    
    metatile_info = REPLICATE( field_info_blank, n_field_side, n_field_side ) 
    
    image_single = {raw:fltarr(n_pix_field,n_pix_field,n_file_max),$
                    s:fltarr(n_pix_field,n_pix_field,n_file_max),$
                    l:fltarr(n_pix_field,n_pix_field,n_file_max)}

    metatile_image = REPLICATE( image_single, n_field_side, n_field_side ) 

    my_n_field = n_field_side^2
    ;; LIMIT:
;    my_n_field = 10
    for i_field_general=0,my_n_field-1 do begin
 
        COUNTER,i_field_general,my_n_field-1

        i_field = i_field_general mod n_field_side
        j_field = i_field_general/n_field_side
        
        file_cube = 'datacube_F' + string(format='(i2.2,i2.2)',i_field,j_field) + '.idl'
        RESTORE,path_metatile_IDL+file_cube

        field_map = map[i_field,j_field]
        n_file = field_map.n_file

        metatile_image[i_field,j_field].raw[*,*,0:n_file-1] = field_list
        
        field_info = field_info_blank  ;; otherwise we keep info from older fields processed.
        ANALYZE_FIELD_LIST,field_map,field_list,$
          field_info,field_list_extra

        metatile_image[i_field,j_field].s[*,*,0:n_file-1] = field_list_extra[*,*,*,0]
        metatile_image[i_field,j_field].l[*,*,0:n_file-1] = field_list_extra[*,*,*,1]
        
        metatile_info[i_field,j_field] = field_info
        
    endfor

    SAVE,filename=PATH_METATILE_IDL+filename_datacube,metatile_info,metatile_image,map
endif


if user_choice eq 2 then restore,path_metatile_idl + filename_datacube

choice_int = 1
i_field_general = 0
i_field = 0
j_field = 0
WHILE (choice_int ne -9) do begin
    
    my_menu:

    print,'----------------'
    print,'00; current'
    print,'10: next'
    print,'0: raw image, 1: small scales, 2: large scales'
    print,'-1: choose coordinate'
    print,'-9: exit'
    read,': ',choice_int

    if choice_int eq -9 then break
    if choice_int/10 eq 1 then begin
        i_field_general++
        i_field = i_field_general mod n_field_side
        j_field = i_field_general/n_field_side
    endif

    if choice_int eq -1 then begin
        read,'i_field=',i_field
        read,'j_field=',j_field
    endif


    field_info = metatile_info[i_field,j_field]
    field_map = map[i_field,j_field]
    n_file = field_map.n_file

    choice_image_type = choice_int mod 10
    field_list_to_display = metatile_image[i_field,j_field].raw[*,*,0:n_file-1]
    if choice_image_type eq 1 then field_list_to_display = metatile_image[i_field,j_field].s[*,*,0:n_file-1]
    if choice_image_type eq 2 then field_list_to_display = metatile_image[i_field,j_field].l[*,*,0:n_file-1]

    print,'coordinates:',i_field,j_field
    print,'found: ',n_file,' files'
    print,'choice_image_type=',choice_image_type

    DISPLAY_INFO,field_map,field_list_to_display,field_info,charsize=charsize,n_field_side,$
      metatile_image[i_field,j_field].s[*,*,0:n_file-1],choice_image_type

endwhile

end

