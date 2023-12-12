from setuptools import setup, find_packages

setup(
    name='binner',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy==1.26.1',
        'opencv-python-headless==4.8.1.78',
        'scipy==1.11.3',
        'scikit-image==0.21.0',
    ],
)