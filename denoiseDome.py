from n2v.models import N2V
import numpy as np
from csbdeep.io import save_tiff_imagej_compatible
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator


dome_path = './domes/Nice Domes' # Fill with the path of the dome
name_of_dome = '21.tif' # Fill with the name of the dome
save_dome_path = './domes/domes_n2v/' # Fill with the path to save the dome
name_save_dome = '21_denoised.tif' # Write the name of the file to save
# The frame number must go from 1 to the maxim frame or -1 to denoise all the frames.
frame = -1 # Write the frame number

datagen = N2V_DataGenerator()
img = datagen.load_imgs_from_directory(directory=dome_path, filter=name_of_dome, dims='TZXY')

print(img[0].shape)

model_name = '2d_images_from_stack'
# The path of the model direcory is relative to this file's path
basedir = './n2v_models/'
model = N2V(config=None, name=model_name, basedir=basedir)

def denoise(img):
    '''
    Return a 3d stack n2v plane by plane.
    '''
    d3_pred = []
    for image in img:
        image = image[:, :, 0]
        non_zero_cols = np.any(image != 0, axis = 0)
        first_non_zero_col = np.argmax(non_zero_cols)
        last_non_zero_col = len(non_zero_cols) - np.argmax(non_zero_cols[::-1]) - 1
        clean_image = image[:, first_non_zero_col:last_non_zero_col + 1]
        pred = model.predict(clean_image, axes='YX')
        full_pred = np.zeros_like(image)
        full_pred[:, first_non_zero_col:last_non_zero_col + 1] = pred
        d3_pred.append(full_pred)
    return d3_pred

stack = []
if frame == -1:
    for im in img[0]:
        stack.append(denoise(im))
elif frame < img[0].shape[0] and frame > -1:
    for im in img[0][frame]:
        stack.append(denoise(img))
elif frame > img[0].shape[0] or frame <= 0:
    print('no frame')
stack = np.array(stack)

save_tiff_imagej_compatible(str(save_dome_path)+str(name_save_dome), stack, axes='TZXY')