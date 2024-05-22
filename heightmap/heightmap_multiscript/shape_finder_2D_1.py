import numpy as np
import common_functions
from scipy.ndimage import rotate
import multiprocessing
import sys
import skimage as sk
import tifffile as tiff
import warnings
from functools import partial
from joblib import Parallel, delayed



def shape_finder_2D_v2(hull_lines, hull_mask, sum_lines, sum_mask, angle=40):
    '''
    Get the first approximation using hull and sum lines, delta degree = 20º
    - hull_lines is the epithelial obtained from hull mask
    - hull_mask is the gaussian or the line obtained using hull from front
    - sum_lines is the epithelial obtained from sum mask
    - sum_mask is the gaussian or the line obtained using hull from front
    - angle is the max rotation for the 2D image
    '''
    angles = [i for i in range(-angle, angle+1, 20)]
    # angles = [40]
    total_cell_mask = np.zeros(shape=(hull_lines.shape))

    for angle in angles:

        ## Rotate the masked image.        
        rot_hull_lines = rotate(hull_lines, angle, reshape=False) # Be careful of the reshape=False
        rot_hull_mask = rotate(hull_mask, angle, reshape=False)
        rot_sum_lines = rotate(sum_lines, angle, reshape=False)
        rot_sum_mask = rotate(sum_mask, angle, reshape=False)
        cell_border = []

        ## Get the position of the maximum intensity.
        for i in range(rot_hull_lines.shape[1]):
            col_hull_lines = rot_hull_lines[:, i]
            max_pos_hull_lines = np.argmax(col_hull_lines == max(col_hull_lines))
            col_hull_mask = rot_hull_mask[:, i]
            max_pos_hull_mask = np.argmax(col_hull_mask == max(col_hull_mask))

            col_sum_lines = rot_sum_lines[:, i]
            max_pos_sum_lines = np.argmax(col_sum_lines == max(col_sum_lines))
            col_sum_mask = rot_sum_mask[:, i]
            max_pos_sum_mask = np.argmax(col_sum_mask == max(col_sum_mask))

            # print(max_pos_hull_lines, max_pos_hull_mask, abs(max_pos_hull_lines-max_pos_hull_mask)/max_pos_hull_mask)


            #   Check that the position is lower than the col ------ Check that the position is grater than the bottom -- 
            if ((max_pos_hull_lines <= len(col_hull_lines)*0.90) and (max_pos_hull_lines >= len(col_hull_lines)*0.1) and 
                # Check that the column has some variation 3 is super conservative ------- Check the distance to the original line
                (max(col_hull_lines) >= col_hull_lines.mean()+3*col_hull_lines.std()) and (abs(max_pos_hull_lines-max_pos_hull_mask)/max_pos_hull_mask >= 0.05)): # 3 IS SUPER CONSERVATIVE
                cell_border.append(max_pos_hull_lines) # Search for the first max

            #   Check that the position is lower than the col ------ Check that the position is grater than the bottom -- 
            elif ((max_pos_sum_lines <= len(col_sum_lines)*0.90) and (max_pos_sum_lines >= len(col_sum_lines)*0.1) and 
                # Check that the column has some variation 3 is super conservative ------- Check the distance to the original line
                (max(col_sum_lines) >= col_sum_lines.mean()+2*col_sum_lines.std()) and (abs(max_pos_sum_lines-max_pos_sum_mask)/max_pos_sum_mask >= 0.05)): # 3 IS SUPER CONSERVATIVE
                cell_border.append(max_pos_sum_lines) # Search for the first max

            else:
                cell_border.append('-')
                # cell_border.append(max_pos_sum_lines) 

        ## Put the positions in a matrix as we have done with the smoothed line before.
        cell_top_mask_rot = np.zeros_like(rot_hull_lines)
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
direction = sys.argv[2]


epithelial_hull = sk.io.imread(wd+'_hull_top_line_epithelial_0.tif')
hull_top_line = sk.io.imread(wd+'_hull_top_line_0.tif')
epithelial_sum = sk.io.imread(wd+'_sum_top_line_epithelial_0.tif')
sum_top_line = sk.io.imread(wd+'_sum_top_line_0.tif')


epithelial_hull_r = common_functions.get_image_r(epithelial_hull)
hull_top_line_r = common_functions.get_image_r(hull_top_line)
epithelial_sum_r = common_functions.get_image_r(epithelial_sum)
sum_top_line_r = common_functions.get_image_r(sum_top_line)



if direction == 'r':
    epithelial_hull_r = np.transpose(epithelial_hull_r, axes=(2,1,0))
    hull_top_line_r = np.transpose(hull_top_line_r, axes=(2,1,0))
    epithelial_sum_r = np.transpose(epithelial_sum_r, axes=(2,1,0))
    sum_top_line_r = np.transpose(sum_top_line_r, axes=(2,1,0))


warnings.filterwarnings("ignore", message="RuntimeWarning: divide by zero encountered in scalar divide")


apical_dots_r = Parallel(n_jobs=-1)(delayed(shape_finder_2D_v2)(i, j, k, l) for i, j, k, l in zip(common_functions.normalize_image(epithelial_hull_r), common_functions.normalize_image(hull_top_line_r), common_functions.normalize_image(epithelial_sum_r), common_functions.normalize_image(sum_top_line_r)))





apical_dots = np.transpose(apical_dots_r, axes=(1,2,0)) # Rotate the surface cells to be viewed from top

if direction == 'r':
    apical_dots = np.transpose(apical_dots, axes=(0,2,1))

apical_dots = apical_dots.astype(np.uint16)

#number 5 is the number of different angles
tiff.imwrite(f'{wd}_apical_dots_{direction}_0.tif', common_functions.normalize_image(apical_dots, 5).astype(np.uint16), imagej=True)