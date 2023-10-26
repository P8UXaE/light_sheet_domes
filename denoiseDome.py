from n2v.models import N2V
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.image import imread, imsave
from csbdeep.io import save_tiff_imagej_compatible
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator


dome_path = './domes/Nice Domes' # Fill with the path of the dome
name_of_dome = '21.tif' # Fill with the name of the dome
save_dome = './domes/domes_n2v/' # Fill with the path to save the dome





print('Denoise 3d dome plane by plane')

datagen = N2V_DataGenerator()
img = datagen.load_imgs_from_directory(directory=dome_path, filter=name_of_dome, dims='TZYX')

print(img[0])
