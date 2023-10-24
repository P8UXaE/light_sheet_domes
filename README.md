To create a new python environment with the desired version:
```{source}
> py -3.11 -m venv venv_tf
> .\ venv_tf\Scripts\activate
```
In order to make git ignore the virtual environments, you must create them with the same name as in ```.gitignore``` file or add the environment name in the file.



Then you can just install tensorflow
```
> pip install tensorflow
```
This way, tensorflow will work using CPU:
```
> python -c "import tensorflow as tf; print(tf.reduce_sum(tf.random.normal([1000, 1000])))"
```
And this way, using GPU: ???
```
>  python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

