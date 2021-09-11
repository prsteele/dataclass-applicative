from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from dataclass_applicative import amap, fmap, gather, names, pure, values
from hypothesis import given
from hypothesis import strategies as st


@dataclass
class F0:
    pass


@dataclass
class F1:
    x: object


@dataclass
class F2:
    x: object
    y: object


@dataclass
class F3:
    x: object
    y: object
    z: object


@dataclass
class G4(F3):
    w: object


@dataclass(frozen=True)
class FrozenF2:
    x: object
    y: object


arbitrary_dataclass_class = st.sampled_from((F0, F1, F2, F3, G4, FrozenF2))


@st.composite
def arbitrary_dataclass(draw):
    cls = draw(arbitrary_dataclass_class)

    return cls(**{name: draw(st.integers()) for name in names(cls)})


@dataclass(frozen=True)
class FuncEval:
    """A record of evaluating a function."""

    caller: object
    args: Tuple[object]
    kwargs: Dict[object, object]


def func() -> Callable[..., FuncEval]:
    """Returns a fresh arbitrary function generator.

    This function is used to verify that two pieces of code ultimately
    evaluate to the same value; for example, we could verify that

    >>> f = func()
    >>> [f(i) for i in range(10)] == list(map(f, range(10)))
    True

    In particular, we did not need to conjure up some faked function
    like 'add 1' to use for our test.

    Different functions applied to the same value are not equal:

    >>> f, g, x = func(), func(), object()
    >>> f(x) == g(x)
    False

    The same function applied to different arguments is not equal:

    >>> f(object()) == f(object())
    False

    """

    caller = object()

    def f(*args: object, **kwargs: object) -> FuncEval:
        return FuncEval(caller, args, kwargs)

    return f


def compose(f):
    """Ordinary function composition."""

    def inner(g):
        def fg(x):
            return f(g(x))

        return fg

    return inner


def identity(x):
    """The identify function."""
    return x


def apply(*args, **kwargs):
    """A function that applies arguments to a function."""

    def f(g):
        return g(*args, **kwargs)

    return f


@given(arbitrary_dataclass())
def test_fmap_laws(x) -> None:
    """Verify the functor laws of fmap.

    Law-abiding functors must satisfy

    1. fmap(identity, x) == x
    2. fmap(compose(f)(g), x) == fmap(fmap(g, x), z)

    for arbitrary functions f and g.

    Property (1) encodes that mapping the identity function changes
    nothing; property (2) encodes that function composition commutes
    with fmap.

    """

    # Verify (1)
    assert fmap(identity, x) == x

    # Verify (2)
    f = func()
    g = func()
    assert fmap(compose(f)(g), x) == fmap(f, fmap(g, x))


@given(arbitrary_dataclass())
def test_amap_laws(x):
    """Verify the applicative functor laws of amap.

    Law-abiding applicative functors must satisfy

    1. amap(pure(x, identity), x) == x
    2. amap(pure(x, f), pure(x, z)) == pure(x, f(z))
    3. amap(u, pure(u, z)) == amap(pure(u, apply(z)), u)
    4. amap(amap(amap(pure(u, compose), u), v), x) == amap(u, amap(v, x))

    pure (.) <*> u <*> v <*> w = u <*> (v <*> w)

    From https://en.wikibooks.org/wiki/Haskell/Applicative_functors,
    these properties are called "identity", "homomorphism",
    "interchange", and "composition;" see that link for the motivation
    for these laws.

    Throughout, `f` is an arbitrary function, `z` is an arbitrary
    value, `x` is an arbitrary dataclass, and `u` and `v` are
    arbitrary dataclasses containing functions.

    """

    # Generate arbitrary functions
    f = func()
    g = func()

    # Generate an arbitrary value that is equal only to itself
    z = object()

    # Generate dataclasses filled with arbitrary functions
    u = fmap(apply(), pure(x, func))
    v = fmap(apply(), pure(x, func))

    # Verify (1)
    assert amap(pure(x, identity), x) == x

    # Verify (2)
    assert amap(pure(x, f), pure(x, z)) == pure(x, f(z))

    # Verify (3)
    assert amap(u, pure(u, z)) == amap(pure(u, apply(z)), u)

    # Verify (4)
    assert amap(amap(amap(pure(u, compose), u), v), x) == amap(u, amap(v, x))
