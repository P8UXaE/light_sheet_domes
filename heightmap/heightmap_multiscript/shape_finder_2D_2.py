import numpy as np
from scipy.ndimage import rotate
import sys
import skimage as sk
import common_functions
import warnings
from joblib import Parallel, delayed
import tifffile as tiff
import os
import glob




def shape_finder_2D(epithelial, angle=40):

    warnings.filterwarnings("ignore", message="divide by zero encountered in scalar divide")

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
                cell_border.append(max_pos) # Search for the max
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
dots_version = sys.argv[2]
direction = sys.argv[3]
moveLine = int(sys.argv[4])



### get the lastest epithelial available
epithelial_dots_path = f'{wd}_{dots_version}_epithelial**'
matching_files = glob.glob(epithelial_dots_path, recursive=True)
number_of_files = 0
for file_path in matching_files:

    file_path = file_path.split('epithelial')
    file_path = file_path[1].split('_')
    file_path = file_path[1].split('.')

    if len(file_path) == 2:
        number_of_files += 1




epithelial_dots_path = f'{wd}_{dots_version}_epithelial_{number_of_files-1}.tif'
epithelial_dots = sk.io.imread(epithelial_dots_path)


epithelial_dots_r = common_functions.get_image_r(epithelial_dots)

if direction == 'r':
    epithelial_dots_r = np.transpose(epithelial_dots_r, axes=(2,1,0))



warnings.filterwarnings("ignore", message="RuntimeWarning: divide by zero encountered in scalar divide")


apical_dots_r = Parallel(n_jobs=-1)(delayed(shape_finder_2D)(i) for i in epithelial_dots_r)


apical_dots = np.transpose(apical_dots_r, axes=(1,2,0)) # Rotate the surface cells to be viewed from top

if direction == 'r':
    apical_dots = np.transpose(apical_dots, axes=(0,2,1))

apical_dots = apical_dots.astype(np.uint16)

if moveLine != 0:
    apical_dots = common_functions.move3D_array(apical_dots, moveLine=moveLine)

#number 5 is the number of different angles
tiff.imwrite(f'{wd}_apical_dots_{direction}_{number_of_files}.tif', common_functions.normalize_image(apical_dots, 9).astype(np.uint16), imagej=True)













