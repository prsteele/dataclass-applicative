Example: manipulating 2-dimensional points
==========================================

As a motivating example, consider a dataclass defining 2-dimensional
points:

>>> from dataclasses import dataclass
>>> from typing import Generic, Iterable, List, Tuple, TypeVar
>>> T = TypeVar("T")
>>> @dataclass
... class Point(Generic[T]):
...     x: T
...     y: T

To manipulate these points, we might want to support translation;

>>> def translate_point(p: Point[float], offset: Point[float]) -> Point[float]:
...     return Point(p.x + offset.x, p.y + offset.y)
>>> translate_point(Point(1, 2), Point(3, 4))
Point(x=4, y=6)

scaling;

>>> def scale_point(p: Point[float], scale: float) -> Point[float]:
...     return Point(p.x * scale, p.y * scale)
>>> scale_point(Point(1, 2), 3)
Point(x=3, y=6)

pretty-printing;

>>> def format_point(p: Point[float]) -> Point[str]:
...     return Point(f'{p.x:.2f}', f'{p.y:.2f}')
>>> format_point(Point(1.111, 2.222))
Point(x='1.11', y='2.22')

and gathering coordinates:

>>> def gather_points(points: Iterable[Point[T]]) -> Point[List[T]]:
...     xs = []
...     ys = []
...     for point in points:
...         xs.append(point.x)
...         ys.append(point.y)
...     return Point(xs, ys)
>>> gather_points(map(Point, range(0, 5), range(5, 10)))
Point(x=[0, 1, 2, 3, 4], y=[5, 6, 7, 8, 9])

None of these functions are complicated, but each requires accessing
`x` and `y` by name which introduces the potential for typos to creep
in. Additionally, we are applying the same operation to each point
every time; we can do better. Using imports from `dataclass_applicative`, 

>>> import operator
>>> from dataclass_applicative import fmap, gather

we could instead write

>>> def translate_point(p: Point[float], offset: Point[float]) -> Point[float]:
...     return fmap(operator.add, p, offset)
>>> translate_point(Point(1, 2), Point(3, 4))
Point(x=4, y=6)

to define translation,

>>> def scale_point(p: Point[float], scale: float) -> Point[float]:
...     return fmap(lambda x: x * scale, p)
>>> scale_point(Point(1, 2), 3)
Point(x=3, y=6)

to define scaling,

>>> def format_point(p: Point[float]) -> Point[str]:
...     return fmap('{:.2f}'.format, p)
>>> format_point(Point(1.111, 2.222))
Point(x='1.11', y='2.22')

to define pretty-printing, and

>>> def gather_points(points: Iterable[Point[T]]) -> Point[Tuple[T]]:
...     return gather(*points)
>>> gather_points(map(Point, range(0, 5), range(5, 10)))
Point(x=(0, 1, 2, 3, 4), y=(5, 6, 7, 8, 9))

to define gathering coordinates. Note that these definitions:

1. cannot mix up operations between the `x` and `y` fields;
2. continue working if you refactor the names of `x` or `y`;
3. continue working if you add additional dimensions to your `Point`.
