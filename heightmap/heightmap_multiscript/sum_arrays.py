import skimage as sk
import sys
import tifffile as tiff

wd = sys.argv[1]
array_name = sys.argv[2]
version = sys.argv[3]

array_path1 = wd +'_'+array_name+'_n_'+version+'.tif'
array_path2 = wd +'_'+array_name+'_r_'+version+'.tif'
array_sum = sk.io.imread(array_path1)+sk.io.imread(array_path1)


array_sum_path = wd +'_'+array_name+'_total_'+version+'.tif'
tiff.imwrite(array_sum_path, array_sum, imagej=True)
