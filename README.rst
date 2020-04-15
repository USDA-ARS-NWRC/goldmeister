===========
Goldmeister
===========


.. image:: https://img.shields.io/pypi/v/goldmeister.svg
        :target: https://pypi.python.org/pypi/goldmeister

.. image:: https://readthedocs.org/projects/goldmeister/badge/?version=latest
        :target: https://goldmeister.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


Welcome!
--------

Goldmeister is a Python package designed to manage/examine changes to a gold
file.

Whats a Gold File?
------------------

A gold file is a dataset that is being used to confirm that a code set is
behaving the same way before changes. Typically they are produced at some point
in time by the software and checked into a repo to use for comparison during
future code changes.


What does Goldmeister do?
-------------------------

When you need to change a gold file, developers can use Goldmeister to quickly
show the changes that are occurring and how.

* Free software: MIT license
* Documentation: https://goldmeister.readthedocs.io.


Features
--------

* Bounce between git branches and check files.
* Compare difference files
* Plot analysis on how data is changing.
* Supports netCDF only


Credits
-------

Developed at the USDA-ARS-NWRC for maintaining scientific code sets where
repeatability is extremely important and thus Gold file affluent.

This package was created with Cookiecutter_ and the
`audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
