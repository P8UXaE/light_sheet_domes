import numpy as np
from scipy.ndimage import rotate
import sys
import skimage as sk
import common_functions
import warnings
from joblib import Parallel, delayed
import tifffile as tiff
import subprocess


def shape_finder_2D(epithelial, angle=40):
    '''
    Falling line algorithm for 2D front image rotation, delta degree = 20º
    - epithelial is the 2D image that has to be fed from front
    - angle is the max rotation for the 2D image
    '''

    angles = [i for i in range(-angle, angle+1, 10)]
    # angles = [-40]
    total_cell_mask = np.zeros(shape=(epithelial.shape))

    for angle in angles:

        ## Rotate the masked image.        
        rot_height_mask = rotate(epithelial, angle, reshape=False) # Be careful of the reshape=False
        ## Find the border of the cell which is the maximum of this masked image.
        cell_border = []

        ## Get the position of the maximum intensity.
        for i in range(rot_height_mask.shape[1]):
            col = rot_height_mask[:, i]
            max_pos = np.argmax(col == max(col))

            if max_pos <= len(col)*0.95 and max_pos >= len(col)*0.05 and max(col) >= col.mean()+2*col.std(): # 3 IS SUPER CONSERVATIVE
                cell_border.append(max_pos) # Search for the first max
            else:
                cell_border.append('-')

        ## Put the positions in a matrix as we have done with the smoothed line before.
        cell_top_mask_rot = np.zeros_like(rot_height_mask)
        for i in range(cell_top_mask_rot.shape[1]):
            if cell_border[i] != '-':
                cell_top_mask_rot[cell_border[i], i] = 1

        ## Rotate the matrix to have it horizontal as the original image.
        cell_top_mask_rot = rotate(cell_top_mask_rot, -angle, reshape=False)
        cell_top_mask_rot[cell_top_mask_rot < 0] = 0
        horizontal_cut = 4
        cell_top_mask_rot[:, :horizontal_cut] = 0
        cell_top_mask_rot[:, -horizontal_cut:] = 0
        total_cell_mask += cell_top_mask_rot

    return np.array(total_cell_mask)



wd = sys.argv[1]
dots_file = sys.argv[2]
move_dots = int(sys.argv[3])

total_dots = sk.io.imread(wd+'_apical_'+dots_file+'dots_1.tif')+sk.io.imread(wd+'_apical_'+dots_file+'dots_2.tif')

image = common_functions.load_image(wd + '.tif')

total_dots = common_functions.move3D_array(total_dots, move_dots)


gaussian_hull_top_line = common_functions.get_3D_gaussian(total_dots)


hull_top_gaussian_path = f'{wd}_{dots_file}_moved_{str(move_dots)}_top_gaussian.tif'
tiff.imwrite(hull_top_gaussian_path, gaussian_hull_top_line, imagej=True)


gaussian_hull_top_line = common_functions.normalize_image(gaussian_hull_top_line)
epithelial_hull = gaussian_hull_top_line*image

epithelial_hull_path = f'{wd}_{dots_file}_moved_{str(move_dots)}_epithelial.tif'
tiff.imwrite(epithelial_hull_path, epithelial_hull.astype(np.uint16), imagej=True)




