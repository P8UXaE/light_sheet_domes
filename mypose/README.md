# Mypose

To use the developed watershed segmentation, prepare at least a 240, 240, 240 image stack of the cell of interest. Open the jupyer notebook and set the folder and the image_route variables. The program will read the image and plot a middle slice. 

You can center the cell and cut the image even more by filling z, y, x values (the center of the stack) and delta, which is the number of pixels taken from z, y, x value to each direction. 

![data_cube](./visual/data_cube.png)

Once selected the 3D block, the script will run a watershed algorithm on it. It will return a 3D image which contains all the watershed regions found. The image used and the labels found will be stored in 2 different files. Open napari and visualize them. 

By selecting the masks indexes and writing them down in the label_numbers list in the file, it will create a single mask with all the pieces. Later, this information is stored in a file called segment_file-v1.txt in case you need to recover any information since the same algorithm run on the same image will output the same regions. 

CAREFUL: If the cell is not well being detected, try correcting the image by doing some color or gamma correction.  

To recover more of the membrane shape, there is a second part of the algorithm which does watershed again but applying a sobel kernel on the image and removing the mask found before. The output will be a 3D array with the different watershed regions found. Open it in napari and again write the masks indices in label_gradient_numbers. Save the total mask and at the end, the segmentation file will get updated with this label_gradient_numbers for further usage. 


# Napari mask correction / manual segmentation

In order to manually correct a mask open napari and drag the image used to get the segmentation and the obtained mask. Then open the IPython console and write: ```viewer.add_labels(viewer.layers[‘segmented_cell’].data)``` to create a Labels layer. In this layer you can manually draw or erase parts of the mask. Make sure you are using the same label to draw as the mask by clicking the Pick mode and selecting the mask. Switch the blending to additive to see the real image at the background. 

Save the Label file. 


# Blender 4.1

Download the [tif to blender](https://github.com/oanegros/tif2blender) zip. You can follow the installation instructions from github. But basically: 

1. Download the zip. 
1. Inside blender go Edit &rarr; Preferences &rarr; Add-ons. 
1. Click Install and search the zip. 
1. Install it and search it inside the Add-ons screen. 
1. Install tifffile from the import. 

After installation:

1. Press the layout of the scene, press ‘a’ and ‘x’ to remove everything.  
1. Go to the Scene icon in the right menu (it is a cone, a bubble and a ball). 

There you have the tif loader. Select the file. Be careful on the xy pixel size and z pixel size so the image is not distorted.  

In the axes, write zyx if it is a 3d tif. (I have not worked in multiple channel tif). Then press Load TIF. 

Some will have a box and the cell inside and some may not (I did not have it). 

In the top right menu unfold the Mesh icon (inverse orange triangle). There you will see an orange Data icon (like a cloud). This is the cell. You can modify the scale or the dimensions by clicking in the Layout and pressing ‘n’. A Transform menu will pop up in the right. If you write 1, 1, 1, you will have the cell sized 1px = 1m. That is not useful at all. If you write 0,1625 (which comes from 1px = 0,1625µm) in each axis you will have the cell dimensions as 1m = 1µm. 

Add &rarr; Mesh &rarr; Cube. 

In the right menu click the cube mesh. Go to modifiers &rarr; Add Modifier &rarr; Generate &rarr; Volume to Mesh.  

Click the Eyedropper Data-Block from the Object. Select the data of your cell (the orange cloud). In Grid Name write ‘channel 0’. If this does not work check the channel name of your data.  

Go on your orange Data icon (the cloud one) and unfold it. You will see the same icon but just with a green outer line. Press it.  

Press the same icon (Data, Object Data Properties) from the bottom right menu. 

In Grids, you should have the name of the data. It must be the same as the one from the Grid Name. 

Once you see a pixelated meshed cell, you can create the object. In the modifiers press the arrow next to the camera icon and press Apply. 

You can remove the initial data you imported with tif2blender (take into account that the Scale of the mesh is 1, 1, 1). 

Right Click on the mesh &rarr; Set Origin &rarr; Geometry to origin. You have centered the cell. 

In the left top corner you see Object Mode, Change to Edit Mode. 

Press ‘a’ (to select all the nodes) &rarr; Vertex &rarr; Smooth Vertices. Smooth the pixelated image. We have done Smoothing = 0.500, Repeat = 20. 

To change the color and texture. Shading &rarr; New (in the bottom window that has just popped up). There you can modify and create materials. Change the color, metallic, roughness, etc. 

If you press the viewport shading icon (top right of the window, it is a ball with some reflection) you will have the scene but as it will look when we further render it. 

Add lights via Add &rarr; Light. Select the light you want. You can move it around by pressing ‘n’ and making sure you have selected it in the right menu, or moving it through the Move icon.  

Also add a camera and place it somewhere that when you press ‘F12’ or Render &rarr; Render Image, you see what you want to see.  

Bottom Right menu &rarr; Render &rarr; Film &rarr; Transparent (for transparent background).  

Bottom Right menu &rarr; Output, to play around with size and fps for films. 

Rotate the cell through time: 

The transform menu that pops up when you press ‘n’ in the layout, you see Rotation. 

Write #frame/57.295 in the axis you want to have the cell rotating. 

At the bottom you see the time bar. Write the frames you want to render where it says End. 

Render a film: Right bottom menu &rarr; Output &rarr; Output &rarr; Select the folder, and file format (AVI JPEG). Press Ctrl+’F12’  or Render &rarr; Render Animation to render the film. More quality: Bottom Right Menu &rarr; Render &rarr; Render Engine &rarr; Cycles. 

