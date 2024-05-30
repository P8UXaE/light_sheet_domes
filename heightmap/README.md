# Heightmap

NOT COMPLETED AT ALL. It may work in some cases where images are good enough, where images are well denoised, the diagonal line that appears when rotating the data does not influence at all and cells are as uniformelly stained as possible. Also known as __GOOD__ IMAGES.

Nontheless, I developed another way to achieve good results when working with deflated domes, wrinkled cells and wrinkled tissue.


# Initial top mask

This methods needs a human input before detecting the apical. Here are the steps to get this first input from an image named ```image_99_denoised_tp4```:

1. Load the image with name: image_99_denoised_tp4 
1. Open IPython Console and inside:
1. Write ```image = viewer.layers['image_99_denoised_tp4'].data``` to put the image inside the variable 
1. ```Import numpy as np```
1. ```mask = np.zeros(image.shape, dtype=np.uint8)```
1. ```viewer.add_image(mask, name='mask')```
1. ```viewer.add_labels(viewer.layers['mask'].data)```
1. This will generate a label data that you can paing on. You should draw the top of the apical (more or less) at y and x direction. As you can see it is not super precise, in fact, it is a more or less delimitation with a brush of 10 px wide.

![manual_apical](./visual/manual_apical.png)

After that you are set to run the file that takes this manual input as the initial guess, then it blurs it and uses it to find the apical shape.




To generate a heightmap of a tissue we first run dottamine on the data and then do the falling line.

# Benchmark

To benchmark the pipeline we compared the results between ours and LocalZProjector.