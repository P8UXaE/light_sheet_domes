import skimage.filters as sk_filters
from joblib import Parallel, delayed
import common_functions
import tifffile as tiff
import sys
import numpy as np
import skimage as sk
import glob


wd = sys.argv[1]
array_name = sys.argv[2]

image_path = wd + '.tif'


### get the lastest epithelial available
epithelial_dots_path = f'{wd}_{array_name}**'
matching_files = glob.glob(epithelial_dots_path, recursive=True)
number_of_files = 0

for file_path in matching_files:

    file_path = file_path.split(array_name)
    file_path = file_path[1].split('_')
    file_path = file_path[1].split('.')
    if len(file_path) == 2:
        number_of_files += 1



array_to_blur_path = f'{wd}_{array_name}_{number_of_files-1}.tif'
array_to_blur = sk.io.imread(array_to_blur_path)

gaussian = common_functions.get_3D_gaussian(array_3D=array_to_blur)

gaussian_path = f'{wd}_{array_name}_gaussian_{number_of_files-1}.tif'
tiff.imwrite(gaussian_path, gaussian, imagej=True)

gaussian_hull_top_line = common_functions.normalize_image(gaussian)
image = common_functions.load_image(image_path=image_path)
epithelial_hull = gaussian_hull_top_line*image

epithelial_hull_path = f'{wd}_{array_name}_epithelial_{number_of_files-1}.tif'
tiff.imwrite(epithelial_hull_path, epithelial_hull.astype(np.uint16), imagej=True)