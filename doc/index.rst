dataclass-applicative
=====================

This packages provides functions for operating on container-like
`dataclass` instances.

.. toctree::
   :maxdepth: 1

   dataclass_applicative
   point_example
   domain_modeling

Quick start
-----------

Given a dataclass,

>>> from dataclasses import dataclass
>>> from dataclass_applicative import amap, fmap, gather, pure, names, values
>>> @dataclass
... class F:
...     x: object
...     y: object
...     z: object

we can list its fields;

>>> list(names(F))
['x', 'y', 'z']

list its values;

>>> list(values(F(1, 2, 3)))
[1, 2, 3]

default-construct new instances;

>>> pure(F, 1)
F(x=1, y=1, z=1)

apply a function to those values;

>>> fmap(str, F(1, 2, 3))
F(x='1', y='2', z='3')

or apply functions stored in one object to values stored in another;

>>> amap(F(str, lambda _: 999, lambda z: z + 1), F(1, 2, 3))
F(x='1', y=999, z=4)

and gather all attributes from many instances into tuples in a new
object:

>>> gather(F(1, 2, 3), F(10, 11, 12), F(3, 2, 1), F(0, 0, 0))
F(x=(1, 10, 3, 0), y=(2, 11, 2, 0), z=(3, 12, 1, 0))

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
