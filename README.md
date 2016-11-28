# FEL-NLP-IR_2016

Source code for 2016 Information Retrieval homeworks (ÚFAL-taught course for FEL)

We are providing this code to help you get to the "meat" of the assignments faster,
without having to write all the pesky parsing methods.

Installation
============

We assume you have the latest Python version (3.5.2).

(If you don't, get it from Anaconnda!
It's a great distribution that can be installed fully locally (no sudo permission needed),
ready with numpy and scipy and the whole scientific computing stack. Also, it provides
virtual environments through the `conda` tool, which is very much recommended practice.)

Make sure that your locale is set to support UTF-8.

There is a standard Python setup script (`setup.py`) to install. Use `python setup.py --develop`
to have changes to the code in your working directory reflected directly in the installation.
If you do not have `setuptools`, the `--develop` command is unfortunately not at your disposal.

The package name, `npfl103`, is an old designation of a similar course at MFF.
I'm using it because I don't know what your course designation is, plus it seems
quite certain that this will not generate a naming conflict.

First steps
===========

There is an Ipython Notebook file that provides a tutorial:

`tutorial/tutorial.ipynb`

Fire up Jupyter and go through the tutorial to learn the basics. It should take about 20 minutes.
If you do not have Jupyter, you can read the HTML version (`tutorial/tutorial.html`) or use
the Pyhton script version (`tutorial/tutorial.py`).

Note that we assume you have already downloaded the assignment `*.tgz` package that contains
the evaluation script. Although the `tutorial/tutorial-assignment` directory copies the structure
of the assignment package (with just a few files, so that you don't have to wait for anything),
the evaluation was left out -- you're going to need it in the assignment itself anyway, so
why compile it twice?

The tutorial assumes you've successfully compiled the `trec_eval` script
in the `npfl103/eval` directory.