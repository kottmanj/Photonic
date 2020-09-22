from setuptools import setup, find_packages
import os


setup(
    name='photonic',
    version="1.0",
    author='Jakob S. Kottmann',
    author_email='jakob.kottmann@gmail.com',
    install_requires= ['tequila @ git+https://github.com/aspuru-guzik-group/tequila.git@master-setup-fix#egg=tequila' ]
    #packages=find_packages(where='src'),
    #package_dir={'': 'src'}
)
