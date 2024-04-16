from setuptools import setup, find_packages

setup(
    name='dottamine',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'lazy_loader==0.3',
        'networkx==3.2.1',
        'numpy==1.26.2',
        'packaging==23.2',
        'Pillow==10.1.0',
        'scipy==1.11.4',
        'tifffile==2023.12.9',
        'opencv-python==4.8.1.78',
        'scikit-image==0.22.0',
        'matplotlib==3.8.0',
    ],
)