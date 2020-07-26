from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='teUtils',    # This is the name of your PyPI-package.
    packages=['teUtils'],
    version='0.88',        # Update the version number for new releases
    #scripts=['teutilities'],    # The name of your scipt, and also the command you'll be using for calling it
    author='H M Sauro',
    author_email='hsauro@uw.edu',
    url='http://tellurium.analogmachine.org',
    description='Utilities for Tellurium',
    long_description=long_description,
    license='MIT',
    classifiers=[
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python :: 3.6',
       'Programming Language :: Python :: 3.7',
       'Operating System :: OS Independent',
    ],
    install_requires=[
        'tabulate', 'libroadrunner', 'lmfit',
        'numpy', 'tellurium',
    ],
    python_requires='>=3.6',
)
