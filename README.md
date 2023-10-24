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

