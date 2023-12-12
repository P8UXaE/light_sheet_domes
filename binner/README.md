# Binner

Binner is a low quality image feature detector. It works by binning the image, masking and expanding to the original size.

Binner can work with several image types. It can work from 2D images up to 4D images.


## Instalation




## Usage


To use Binner, you just need to import ```skimage``` as the image loader and ```imbin``` as the image processing algorithm.

```
import skimage as sk
from binner import imbin
```

Then you have to load the image and, for instance, get the binary mask of the image.

```
image = sk.io.imread('image route')
processed_image = imbin(...)
processed_mask = processed_image.get_mask(...)
```


## Documentation

### Initialization

To initialize the processing, create an object using the `imbin` class. This class takes the following parameters:

- `image`: A numpy array representing a single image channel. It can be a 2D, 3D, or 4D array.
- `is2D`: A boolean, either `True` or `False` (default is `False`), indicating whether the arrays are 2D or 3D images. When the array has a fourth dimension (time dimension), leave it as `False`.
- `treat_3D_as_2D`: A boolean, either `True` or `False` (default is `False`), determining if you want to process the 3D image slice by slice. If set to `True`, note that it will process the image as the object contains it. This means that if the original image is a top-bottom view (z-axis), the slices will be z slices. If you wish to process slices along other axes individually, you must rotate the image accordingly.


### Functions

#### `conv_deconv` Function

The `conv_deconv` function is designed for iterative binning, masking, and unbinning of an image. It takes the following parameters:

- `times`: An integer representing the number of iterations for binning the image.
- `binshape`: A tuple specifying the shape of the binned pixels. The tuple elements are ordered as follows: (z-axis, y-axis, x-axis).
- `v`: Verbose. Add `'+'` to follow the process.

**Note**: The results of the operation depend on both `times` and `binshape`. It is crucial to choose appropriate values for meaningful outcomes. For instance, creating a mask on a 1px * 1px image may not yield desirable results. Our tests indicate that optimal outcomes are achieved by masking 100px * 100px images that have been binned from an 800px * 800px image three times with a bin shape of (2,2).

#### `get_mask` Function

The `get_mask` function returns a binary mask of the image processing it by binning, masking, unbinning, getting the coordinates, making the delaunay trinagles and filling them before basic morphological operations. It works over the result of the `conv_deconv` function, but there is no need to execute it first. It takes the following parameters:

- `times`: An integer representing the number of iterations for binning the image.
- `binshape`: A tuple specifying the shape of the binned pixels. The tuple elements are ordered as follows: (z-axis, y-axis, x-axis).

**Note**: Those two parameters will only be used if the object does not contain the result of the `conv_deconv` function, otherwise it will use the already computed point image.

- `morph_close_k`: An integer representing the rectangular kernel for the [morphology closing operation](https://docs.opencv.org/3.4/d9/d61/tutorial_py_morphological_ops.html) used to create the mask result. Used if images to process are 2D.
- `morph_open_k`: An integer representing the rectangular kernel for the [morphology opening operation](https://docs.opencv.org/3.4/d9/d61/tutorial_py_morphological_ops.html) used to create the mask result. Used if images to process are 2D.
- `m_ball`: An integer representing the [ball footprint](https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.ball) used for both [closing](https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.binary_closing) and [opening](https://scikit-image.org/docs/stable/api/skimage.morphology.html#skimage.morphology.binary_opening).
- `v`: Verbose. Add `'+'` to follow the process.


