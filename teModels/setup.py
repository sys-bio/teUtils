from setuptools import setup, find_packages

with open("README.txt", "r") as fh:
    long_description = fh.read()

setup(
    name='teModels',    # This is the name of your PyPI-package.
    packages=find_packages(),
    version='0.91',        # Update the version number for new releases
    #scripts=['teutilities'],    # The name of your scipt, and also the command you'll be using for calling it
    author='H M Sauro',
    author_email='hsauro@uw.edu',
    url='http://tellurium.analogmachine.org',
    description='Example Models for Tellurium',
    long_description=long_description,
    include_package_data=True,
    license='MIT',
    classifiers=[
       'License :: OSI Approved :: MIT License',
       'Programming Language :: Python :: 3.6',
       'Programming Language :: Python :: 3.7',
       'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)