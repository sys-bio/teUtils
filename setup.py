from setuptools import find_packages, setup
import os.path
import codecs

with open("README.md", "r") as fh:
    long_description = fh.read()

# The following two methods were copied from
# https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            print (line)
            delim = '"' if '"' in line else "'"
            print ('delim = ', delim)
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='teUtils',    # This is the name of your PyPI-package.
    packages=find_packages(),
    version=get_version("teUtils/_version.py"),   # Update the version number for new releases
    #scripts=['teutilities'],    # The name of your scipt, and also the command you'll be using for calling it
    author_email='hsauro@uw.edu',
    url='https://github.com/sys-bio/teUtils',
    description='Utilities for Tellurium',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python :: 3.7',
       'Programming Language :: Python :: 3.8',
       'Programming Language :: Python :: 3.9',
       'Programming Language :: Python :: 3.10',
       'Programming Language :: Python :: 3.11',
       'Operating System :: OS Independent',
    ],
    install_requires=[
        'tabulate', 
        'numpy>=1.20', 
        'tellurium',
        'libsbml',
        'pandas',
    ],
    python_requires='>=3.7',
)
