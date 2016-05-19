
print,'1: load Beijing 1685-1270'
print,'2: load Dubai   1338-1171'
read,choice
if choice eq 1 then path_metatile = '/scratch/gwln2/menard/DATA/Planet/Beijing/1685-1270/' 
if choice eq 2 then path_metatile = '/scratch/gwln2/menard/DATA/Planet/Dubai/1338-1171/'

path_metatile_FITS = path_metatile + 'FITS/'
path_metatile_IDL = path_metatile + 'IDL/'
;path_metatile_IDL = path_metatile + 'IDL_32/'

n_field_side = (size(map))(1)

choice = 0

restore,path_metatile_IDL + 'map.idl'

MULTIPLOT,/default
erase

plot,[1,2],/nodata,xr=[800,1500],yr=[0,n_field_side^2+2]
i_file_count = 0
for i=0,n_field_side-1 do begin
    for j=0,n_field_side-1 do begin
        n_file = map[i,j].n_file
        oplot,map[i,j].timestamp[0:n_file-1],i_file_count *indgen(n_file),$
          psym=4
        i_file_count++
    endfor
endfor
pause


print,'Coverage ------------------------'
print,MOMENT(map.n_file)
MULTIPLOT,[2,2]
DISPLAY_BM,HIST_EQUAL(map.n_file)
MULTIPLOT,/DEFAULT
print,'---------------------------------'



; ERASE
; MULTIPLOT,[n_i_field,n_j_field]
; for j_field = 0,n_j_field-1 do begin
;     for i_field = 0,n_i_field-1 do begin

;         my_yr = [0,max(map.n_file)]
;         plothist,map[i_field,j_field].coverage_fraction,bin=0.01,xr=[0.1,1.1],/fill,$
;           yr=my_yr
;         oplot,[1,1],my_yr,linestyle=2
;         multiplot

;     endfor
; endfor
pause



ERASE
MULTIPLOT,[n_field_side,n_field_side]

for j_field = 0,n_field_side-1 do begin
    for i_field = 0,n_field_side-1 do begin
        
        file_cube = 'datacube_F' + string(format='(i2.2,i2.2)',i_field,j_field) + '.idl'

        RESTORE,path_metatile_IDL+file_cube

        data = field_list[*,*,1]

        DISPLAY_BM,HIST_EQUAL(data),/noerase
        MULTIPLOT
;        pause

    endfor
endfor

MULTIPLOT,/DEFAULT

end
