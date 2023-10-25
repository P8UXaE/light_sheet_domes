# Environments

To create a new python environment with the desired version:
```{source}
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

You can just install tensorflow
```
> pip install tensorflow
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
