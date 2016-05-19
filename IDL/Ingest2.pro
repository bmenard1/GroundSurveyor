;goto,ici2

print,SYSTIME()

user = {temp:0.,$
        path_data:'/scratch/gwln2/menard/DATA/Planet/',$
;        area_name:'Alberta',$
;        area_name:'SanFrancisco',$
        area_name:'Beijing',$
        filename_datacube:'datacube.idl',$
        n_pix:1024*4,$
        n_pix_field:1024,$
        n_pix_small:128,$
        n_file_max_to_process:80,$
        my_min_fraction_pixels_with_data:0.95,$
        filter_size:10,$
        min_corr_for_match:0.7,$
        n_file_max:2000L,$  ;; to improve later
        n_image_x:3,$
        n_image_y:2,$
        x_metatile:0,$
        y_metatile:0  }



area_name = 'Beijing'
n_field = 16
print,'Number of fields per metatile: ',n_field

n_pix_metatile = 4096
my_coverage_min = 0.9


n_pix_field = n_pix_metatile/n_field

;; -- Define the path of the metatile

path_metatile = '/scratch/gwln2/menard/DATA/Planet/Dubai/1338-1171/'
;path_metatile = '/scratch/gwln2/menard/DATA/Planet/Beijing/1685-1270/' 
path_metatile_FITS = path_metatile + 'FITS/'

print,'Metatile: ',path_metatile_FITS
print,'Area: ',area_name
metatile_path_list = file_search(path_metatile_FITS, 'I*')

;; -- get the list of .fits files from that directory
file_list = file_search( path_metatile_FITS , '*.fit')
n_file_for_this_metatile = n_elements(file_list)
print,'Found ',n_file_for_this_metatile,' files in this metatile'
;; LIMITS:
;n_file_for_this_metatile = 10
print,'Using ',n_file_for_this_metatile,' files in this metatile'



if n_file_for_this_metatile eq 0 then begin
    print,'no .fits files found in directory ',path_metatile_FITS
    stop
endif


print,'-- Ingest all the data into one array...'
    
datacube_master = fltarr(n_pix_metatile,n_pix_metatile, n_file_for_this_metatile)
maskcube_master = lonarr(n_pix_metatile,n_pix_metatile, n_file_for_this_metatile)
;filename_master = STRARR(n_file_for_this_metatile)

for i_file=0L,n_file_for_this_metatile-1 do begin
    
    COUNTER,i_file,n_file_for_this_metatile-1
    
    filename = file_list[i_file]
    image = MRDFITS(filename,/UNSIGNED,/silent)
    
    datacube_master[*,*,i_file] = image[*,*,0]
    maskcube_master[*,*,i_file] = image[*,*,3]
    ;; when mask is set, its value is 65535

endfor

filename_datacube = path_metatile + '/IDL/' + 'datacube_' + '.idl'



ici2:

    print,'Create one datacube fer unit field'
    
    ;; -- the variable map_single contains summary information for
    ;;    each unit field.
    map_single = {n_file:0,$
                  id_file_list:intarr(n_file_for_this_metatile),$
                  filename:strarr(n_file_for_this_metatile),$
                  timestamp:dblarr(n_file_for_this_metatile),$
                  hour:dblarr(n_file_for_this_metatile),$
                  minute:dblarr(n_file_for_this_metatile),$
                  second:dblarr(n_file_for_this_metatile),$
                  sat_ref:strarr(n_file_for_this_metatile),$
                  coverage_fraction:fltarr(n_file_for_this_metatile)}
    map = REPLICATE(map_single, n_field, n_field)
    

    
    for i_field=0,n_field-1 do begin
        
        COUNTER,i_field,n_field-1

        id_x_field = i_field*n_pix_field + indgen(n_pix_field)
        
        for j_field=0,n_field-1 do begin
            
            ;; -- select only the region of the metatile corresponding
            ;;    to the selected field(i,j)
            id_y_field = j_field*n_pix_field + indgen(n_pix_field)
            my_fields = fltarr(n_pix_field,n_pix_field,n_file_for_this_metatile)
            my_fields = datacube_master[id_x_field,id_y_field,*]
            my_fields_mask = maskcube_master[id_x_field,id_y_field,*]*1L


            ;; -- for each file, check if there is enough coverage
            for i_file=0,n_file_for_this_metatile-1 do begin

                id_pix_bad = where( my_fields_mask[*,*,i_file] eq 0,n_pix_bad )
                field_coverage = 1. - 1.d0 * n_pix_bad / ((1.d0*n_pix_field)^2) 
;                print,field_coverage
                map[i_field,j_field].coverage_fraction[i_file] = field_coverage

;                print,i_field,j_field,field_coverage,n_pix_bad
                
                if field_coverage ge my_coverage_min then begin
                    n_file_already_included = map[i_field,j_field].n_file
                    ;; add new filename
                    map[i_field,j_field].id_file_list[n_file_already_included] = i_file
                    filename = file_list[i_file]
                    map[i_field,j_field].filename[n_file_already_included] = filename

                    ;; extract time stamp
                    ;; it should be something like: L15-1685E-1270N.0.20140713_021839_0903.tif.mq.tif.fit
                    ;; Let's assume that .0. will always be there
                    ;; [Check with Frank at some point]
                    sentence = STRSPLIT(filename,'/',/extract)
                    word_with_info = sentence[n_elements(sentence)-1]
                    word_beginning_strimmed = STRMID(word_with_info,18,22)
                    words = STRSPLIT(word_beginning_strimmed,'_',/extract)
                    n_words = n_elements(words)

                    date = words[0]
                    time = words[1]
                    year = STRMID(date,0,4)
                    month = STRMID(date,4,2)
                    day = STRMID(date,6,2)
                    hour = STRMID(time,0,2)
                    minute = STRMID(time,2,2)
                    second = STRMID(time,4,2)

                    if (n_words eq 4) then begin
                        second += float(words[2])*0.1
                        sat_ref = ( STRSPLIT(words[3],'.',/extract) )[0]
                    endif else begin
                        sat_ref = ( STRSPLIT(words[2],'.',/extract) )[0]  
                    endelse
                      
                    my_time_stamp = JULDAY(month,day,year,hour,minute,second) - (1780000+676000)
                    map[i_field,j_field].timestamp[n_file_already_included] = my_time_stamp
                    map[i_field,j_field].hour[n_file_already_included] = hour
                    map[i_field,j_field].minute[n_file_already_included] = minute
                    map[i_field,j_field].second[n_file_already_included] = second
                    map[i_field,j_field].sat_ref[n_file_already_included] = sat_ref
                    map[i_field,j_field].n_file += 1
                endif
            endfor

            
            n_file_to_consider = map[i_field,j_field].n_file
            if n_file_to_consider gt 0 then begin

                field_list = fltarr(n_pix_field,n_pix_field,n_file_to_consider)
                for i_file=0,n_file_to_consider-1 do begin
                    
;                    COUNTER,i_file,n_file_to_consider
                    i_file_from_master = map[i_field,j_field].id_file_list[i_file]
                    
                    ;; -- Get the data and Rotate for standard view
                    field_list[*,*,i_file] = ROTATE(my_fields[*,*,i_file_from_master],7)

                endfor
                
                file_tag_F = string(format='("F",i2.2,i2.2)',i_field,j_field)
                filename_idl_save = path_metatile + '/IDL/' + $
                  'datacube_' + file_tag_F + '.idl'
                
                ;; -- save the field_list (a pile). Expected ~300 MB.
                SAVE,field_list,filename=filename_idl_save
            endif            


        endfor
    endfor
    
    SPAWN,'mkdir ' + path_metatile + '/IDL/'
    my_filename = path_metatile + '/IDL/' + $
      'map.idl'
    
    ;; -- save global information
    SAVE,map,map_high_resolution,filename=my_filename

;    delvar,datacube_master,maskcube_master

print,SYSTIME()
print,'Reached the end.'

end





;; -- Now that all the data is in memory for the metatile, 



;; create coverage map and individual datacubes for future analysis.
    
;    print,'Create high resolution coverage map...'
    
;    words = STRSPLIT(path_metatile metatile_path_list[i_metatile_path],'/',/extract)
;    metatile_ref = words(n_elements(words)-1)

;    i_metatile = STRMID(metatile_ref,1,1)
;    j_metatile = STRMID(metatile_ref,2,1)

;    map_high_resolution = fltarr(n_pix,n_pix)
;    for i_pix=0,n_pix-1 do begin
;        COUNTER,i_pix,n_pix
;        for j_pix=0,n_pix-1 do begin
;            map_high_resolution[i_pix,j_pix] = TOTAL(datacube_master[i_pix,j_pix,3,*])
;        endfor
;    endfor

