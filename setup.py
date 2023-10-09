# Licensed under a 3-clause BSD style license - see License.txt

from setuptools import setup

setup(
    name='firefly_client',
    version='2.9.0',
    description='Python API for Firefly',
    author='IPAC LSST SUIT',
    license='BSD',
    url='http://github.com/Caltech-IPAC/firefly_client',
    packages=['firefly_client'],
    install_requires=['websocket-client', 'requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
