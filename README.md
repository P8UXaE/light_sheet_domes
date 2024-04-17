# Environments

To create a new python environment with the desired version:
```{bash}
> py -3.11 -m venv venv_tf
> .\ venv_tf\Scripts\activate
```
Just deactivate the environment typing:
```
> deactivate
```
In order to make git ignore the virtual environments, you must create them with the same name as in ```.gitignore``` file or add the environment name in the file.

To install all the requirements.txt file, you may just type:
```
> pip install -r requirements.txt
```
Do it inside the desired venv


# Tensorflow (easy)

Tensorflow is a python package that sometimes has incompatibilities with other packages. I recomend creating a new environment and installing tensorflow inside. In this same package you can install n2v.

You can just install tensorflow (check which version of tf works with n2v!)
```
> pip install tensorflow==2.13.

```
This way, tensorflow will work using CPU:
```
> python -c "import tensorflow as tf; print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
```
And this way, using GPU:
```
>  python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```
The default tensorflow does not allow to use GPU independently, so, instead install a previous version if the case.

# Problems I had with github.

The first time I initialized github on the microscopy computer, it automatically created a branch called master. The main branch of the repository is called ```main```.

In the case you want to switch among branches you can do ```$ git checkout main```.

# Github things

To get the lastest version of the documents in the repository:
```
> git pull
```

To upload your files to the repository:
```
> git add .
> git commit -m "Message that will appear in the git repository"
> git push
```
In the ```> git add .``` command, you can just substitute the ```.``` for a filename to just add this file to git.

# Napari

To use napari, just import it, load an image using skimage and initializate the viewer:
```
import napari
import skimage as sk
im = sk.io.imread('Image dir')
viewer = napari.Viewer()
viewer.add_image(im)
```

# N2V for a given dome

The file called ```denoiseDome.py``` (there is a jupyter notebook version of it [not in main]) denoises a dome using a 2d plane denoise model. To make it work, just change the directories. It is kind of slow. For every 2D plane it takes around 1 or 2 seconds, so multiply the number of Z layers per frames and this is the time it will take.
```{py}
dome_path =      './domes/Nice Domes' # Fill with the path of the dome
name_of_dome =   '21.tif'             # Fill with the name of the dome
save_dome_path = './domes/domes_n2v/' # Fill with the path to save the dome
name_save_dome = '21_denoised.tif'    # Write the name of the file to save
```
Also, once you have wwritten the directories, you have to write which 3D frame you want to denoise. If you want to denoise 4D data, just write ```-1```:
```
frame = -1 # Write the frame number (-1) for evety timepoint
```

Be careful with the path of the model. You may need to change it if you move the ```denoiseDome.py``` file. We can train another model using different images of several domes and timepoints in order to make it more adaptable to a given case.

# Cellpose for napari

After installing cellpose for napari (in requirements_pynapari), or ```pip install cellpose-napari```, initializate a napari View. Then go to pluggins, and select ```cellpose (cellpose-napari)```. 
- If it does not appear, close napari and open it again. You can also check if it is installed in Plugins > Install/Uninstall plugins.
- Once you have it and you select it, a panel will appear on the right of the napari viewer. You have to select the image layer you want to segment, and the model. 
- Check process stack as 3D and also, if you want to try several parameters, you may want to uncheck the clear previous results box.
- Then just press run segmentation. It will take around 10 to 15 minutes to process a ~130 image stack.

The problem with cellpose (as all segmentation algorithms) remains in the quality of the image we have. The higher the quality, the better the results.