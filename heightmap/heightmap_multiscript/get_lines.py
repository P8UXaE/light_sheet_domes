import skimage as sk
import matplotlib.pyplot as plt
from dottamine import dotim
import numpy as np
import cv2
from scipy.ndimage import gaussian_filter, rotate, gaussian_filter1d
import tifffile as tiff
import multiprocessing
from multiprocessing import Pool
import common_functions
import os
import warnings
from concurrent.futures import ThreadPoolExecutor
from joblib import Parallel, delayed
import skimage.filters as sk_filters
import sys





# time_dome = str(4)
# folder_and_dome = str('./../../../../Desktop/dome70_fallinglineMove/70_denoised_tp')

wd = sys.argv[1]

image_path = wd + '.tif'

image = common_functions.load_image(image_path=image_path)

image_r = common_functions.get_image_r(image)

mask_path = wd +'_mask.tif'

##### LOAD MASK #####
if os.path.isfile(mask_path):
    mask_r = sk.io.imread(mask_path)
    print("Mask successfully loaded.")
else:
    doter = dotim(image_r, is2D=False, treat_3D_as_2D=False) #### image or image_r
    mask_r = doter.get_mask(times=3, binshape=(2,2,2), v='+') # Get the mask from side front
    mask_r = mask_r.astype(np.uint16) # Make the mask uint16
    tiff.imwrite(mask_path, common_functions.normalize_image(mask_r, 1).astype(np.uint16), imagej=True)




##### GET CLOSED MASK #####
closed_mask_r = []
for i in mask_r:
    full = cv2.morphologyEx(i, cv2.MORPH_CLOSE, np.ones((10, 10)))
    closed_mask_r.append(full)

closed_mask = np.array(closed_mask_r) # Mask once closed

##### GET CLOSED MASK #####
## Find the top line of the mask
first_nonzero_indices = np.argmax(closed_mask != 0, axis=1)
top_mask = np.zeros_like(closed_mask) # Line from top
top_mask[np.arange(closed_mask.shape[0])[:, None, None], first_nonzero_indices[:, None, :], np.arange(closed_mask.shape[2])] = 1 # Top mask is a 3D array that contains the top line of the actual mask

## Find the left line of the mask
first_left_nonzero_indices = np.argmax(closed_mask != 0, axis=2)
left_mask = np.zeros_like(closed_mask) # Line from left
left_mask[np.arange(closed_mask.shape[0])[:, None, None], np.arange(closed_mask.shape[1]), first_left_nonzero_indices[None, :, None]] = 1 # Top mask is a 3D array that contains the left line of the actual mask

## Find the right line of the mask
last_right_nonzero_indices = closed_mask.shape[2] - np.argmax(closed_mask[:, :, ::-1] != 0, axis=2) - 1
right_mask = np.zeros_like(closed_mask) # Line from right
right_mask[np.arange(closed_mask.shape[0])[:, None, None], np.arange(closed_mask.shape[1]), last_right_nonzero_indices[None, :, None]] = 1 # Right mask is a 3D array that contains the right line of the actual mask

sum_mask = top_mask+left_mask+right_mask # Sum of lines from top
# Make the first and last for each axis 0.
sum_mask[0, :, :] = 0
sum_mask[-1, :, :] = 0
sum_mask[:, 0, :] = 0
sum_mask[:, -1, :] = 0
sum_mask[:, :, 0] = 0
sum_mask[:, :, -1] = 0

sum_mask = np.transpose(sum_mask, axes=(1,2,0)) # Sum viewed from top

sum_top_line_path = wd +'_sum_top_line_0.tif'
tiff.imwrite(sum_top_line_path, sum_mask, imagej=True)

# sum_mask_r = common_functions.get_image_r(sum_mask)


warnings.filterwarnings("ignore", message="Input image is entirely zero, no valid convex hull. Returning empty image")

##### GET HULL #####
def get_hull_from_top(i, num):
    hull_i = sk.morphology.convex_hull_image(i)
    return num, hull_i

return_dict = {}
max_jobs = 5  # Change this to the maximum number of concurrent processes you want
pool = multiprocessing.Pool()  # Use all available cores
results = [pool.apply_async(get_hull_from_top, args=(i, num)) for num, i in enumerate(sum_mask)]
pool.close()
pool.join()

# Get results in order
return_dict = {}
for result in results:
    num, hull_i = result.get()
    if hull_i is not None:
        return_dict[num] = hull_i

hull = np.array([return_dict[idx] for idx in sorted(return_dict.keys())]).astype(np.uint8)

# hull_path = wd + '_hull.tif'
# tiff.imwrite(hull_path, hull.astype(np.uint16), imagej=True)


hull_r = common_functions.get_image_r(hull)

##### MOVE LINE ON!!!! #####
moveLine=0
hull_top_line_r = common_functions.first_nonzero(hull_r, axis=1, moveLine=moveLine) # This is the top line of hull_r
hull_top_line = np.transpose(hull_top_line_r, axes=(1,2,0)) # This is the top hull line viewed from top

hull_top_line = hull_top_line.astype(np.uint16)*65535

hull_top_line_path = wd +'_hull_top_line_0.tif'
tiff.imwrite(hull_top_line_path, hull_top_line, imagej=True)




##### GET GAUSSIANS, EPITHELIALS #####
# hull_top_line = hull_top_line.astype(np.float64)
# gaussian_hull_top_line = gaussian_filter(hull_top_line, 20)
# gaussian_hull_top_line = common_functions.normalize_image(gaussian_hull_top_line)
# epithelial_hull = gaussian_hull_top_line*image # The gaussian cells viewed from top obtained using hull








# sum_mask = sum_mask.astype(np.float64)
# gaussian_sum_mask = gaussian_filter(sum_mask, 20)
# gaussian_sum_mask = common_functions.normalize_image(gaussian_sum_mask)
# epithelial_sum = gaussian_sum_mask*image  # The gaussian cells viewed from top obtained using sum lines