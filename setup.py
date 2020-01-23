from setuptools import setup, find_packages
import os


setup(
    name='photonic',
    version="XXXX",
    author='Jakob S. Kottmann',
    author_email='jakob.kottmann@gmail.com',
    install_requires=requirements,
    packages=find_packages(include=['photonic']),
    package_dir={'': 'photonic'},
    include_package_data=True,
    package_data={
        '': [os.path.join('photonic')]
    }
)
