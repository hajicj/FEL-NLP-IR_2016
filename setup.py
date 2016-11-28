from __future__ import print_function, unicode_literals
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='npfl103',
    version='1.0.0',
    packages=['npfl103'],
    url='https://github.com/hajicj/FEL-NLP-IR_2016',
    license='Apache 2.0',
    author='Jan Hajic jr.',
    author_email='hajicj@ufal.mff.cuni.cz',
    description='Source code for Information Retrieval homeworks (UFAL-taught course for FEL) '
)
