import skimage as sk
import numpy as np
from joblib import Parallel, delayed
import skimage.filters as sk_filters


def normalize_image(im, mult_factor = 1):
    '''
    Normalize image (any Dimensions) function.
    '''
    im = np.array(im)
    if im.max() == 0 and im.min() == 0:
        norm_im = np.zeros((im.shape))
    else:
        norm_im = (im - im.min()) / (im.max()-im.min()) * mult_factor
    return norm_im

def reverse_values(im):
    rev_im = im.max()-im
    return rev_im

def first_nonzero(d3_array, axis=0, moveLine=0):
    '''
    Get a line from a mask (3d array). 
    - axis can be 0, 1, 2. 
    - moveLine is the amount of pixels you want to move the line up or down.
    '''

    first_nonzero_indices = np.argmax(d3_array != 0, axis=axis)

    ## Move up or down the line
    first_nonzero_indices = first_nonzero_indices+moveLine # Units to move the line. If > 0  the line will be lower, useful to get the basal? If < 0 the line will be higher, useful for apical.
    first_nonzero_indices[first_nonzero_indices < 0] = 0
    first_nonzero_indices[first_nonzero_indices >= d3_array.shape[1]] = d3_array.shape[1]-1
    ## Fi move up or down the line

    top_mask_r = np.zeros_like(d3_array)
    top_mask_r[np.arange(d3_array.shape[0])[:, None, None], first_nonzero_indices[:, None, :], np.arange(d3_array.shape[2])] = 1 # Top mask is a 3D array that contains the top line of the actual mask
    if axis==0:
        top_mask_r[0,:,:] = 0
    if axis==1:
        top_mask_r[:,0,:] = 0
    if axis==2:
        top_mask_r[:,:,0] = 0

    return top_mask_r

def get_image_r(image):
    image_r = np.transpose(image, axes=(1,0,2))
    image_r = np.transpose(image_r, axes=(2, 1, 0)) # Image from side front

    return image_r

def move3D_array(array, moveLine):
    if moveLine > 0:
        array = array[moveLine:]
        zeros = np.zeros((moveLine, array.shape[1], array.shape[2]), dtype=array.dtype)
        array = np.vstack((array, zeros))

    elif moveLine < 0:
        array = array[:moveLine]
        moveLine = abs(moveLine)
        zeros = np.zeros((moveLine, array.shape[1], array.shape[2]), dtype=array.dtype)
        array = np.vstack((zeros, array))
    
    return array


def move2D_array(array, moveLine):
    if moveLine > 0:
        array = array[moveLine:]
        zeros = np.zeros((moveLine, array.shape[1]), dtype=array.dtype)
        array = np.vstack((array, zeros))

    elif moveLine < 0:
        array = array[:moveLine]
        moveLine = abs(moveLine)
        zeros = np.zeros((moveLine, array.shape[1]), dtype=array.dtype)
        array = np.vstack((zeros, array))
    
    return array



def load_image(image_path):
    ##### LOAD THE IMAGE #####
    try:
        image = sk.io.imread(image_path)  # Image from top
        # with open(image_path, 'rb') as f:
            # image = sk.io.imread(f)  # Image from top
        # print(image.shape)
        print("Image successfully loaded.")
        return image
    except FileNotFoundError:
        print(f"File {image_path} not found.")
    except Exception as e:
        print(f"Error loading image: {e}")


def gaussian_2D(i, sigma):
    blurred_i = sk_filters.gaussian(i, sigma=sigma, mode='nearest')
    return blurred_i

def run_2D_gaussian(array_2D, sigma):
    return Parallel(n_jobs=-1)(delayed(gaussian_2D)(i, sigma) for i in array_2D)

def get_3D_gaussian(array_3D, sigma_single=20):

    # Apply 2D Gaussian blur along X and Y axes
    blurredXY = run_2D_gaussian(array_3D, sigma=(sigma_single, sigma_single))
    blurredXY_r = get_image_r(np.array(blurredXY))

    # Apply 1D Gaussian blur along Z axis
    blurredXYZ_r = run_2D_gaussian(blurredXY_r, sigma=(sigma_single, 0))

    # Transpose the result to have the correct dimensions
    blurredXYZ = np.transpose(np.array(blurredXYZ_r), axes=(1, 2, 0))
    blurredXYZ = normalize_image(blurredXYZ, 65535).astype(np.uint16)

    return blurredXYZ



def get_heightmap(d3array):
    max_intensity_indices = np.argmax(d3array, axis=0)
    return max_intensity_indices

