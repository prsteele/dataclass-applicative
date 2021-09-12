Example: modeling a problem domain
==================================

The :ref:`2-dimensional points<2D points>` example is somewhat
stylized; most real-world applications contain more interesting
domains to model. This example will model a more involved domain ---
an analysis of baseball games.

Let us begin with classes modeling players, positions, innings, and games:

>>> from enum import Enum, auto
>>> from dataclasses import dataclass
>>> from typing import Dict, List, Optional, Tuple, Set
>>> class Position(Enum):
...     pitcher = auto()
...     catcher = auto()
...     first_base = auto()
...     second_base = auto()
...     third_base = auto()
...     shortstop = auto()
...     left_field = auto()
...     center_field = auto()
...     right_field = auto()
...     designated_hitter = auto()
>>> @dataclass
... class Player:
...     name: str
...     positions: Set[Position]
>>> @dataclass
... class Team:
...     name: str
...     roster: List[Player]
>>> @dataclass
... class Half:
...     inning_number: int
...     field: Dict[Position, Player]
...     lineup: List[Player]
>>> @dataclass
... class Inning:
...     top: Half
...     bottom: Half
>>> @dataclass
... class Game:
...     home: Team
...     away: Team
...     innings: Dict[int, Inning]

As written, we don't have a single dataclass here that can be used
with `dataclass_applicative` correctly --- none of the classes are
even generic over their arguments! Although Python would permit us to
`fmap` over a `Player`, the function we provide would need to be able
to operate on both strings (the `name` field) and a set of `Position`
(the `positions` attribute.) Code written this way is likely to be
brittle and difficult to read.

However, there is a dataclass we could add which would likely be
useful for all manner of inquiries, which is

>>> from typing import Generic, TypeVar
>>> T = TypeVar('T')
>>> @dataclass
... class Positions(Generic[T]):
...     pitcher: T
...     catcher: T
...     first_base: T
...     second_base: T
...     third_base: T
...     shortstop: T
...     left_field: T
...     center_field: T
...     right_field: T
...     designated_hitter: T

This class looks superficially similar to the `Position` enumeration,
but they serve entirely different purposes. The `Position` enumeration
allows us to refer to any particular position symbolically, while the
`Positions` class allows us to associate arbitrary values with each
fielding position. [#f1]_ First, we can replace our definition of `Half` with
the more rigorous

>>> @dataclass
... class Half:
...     field: Positions[Player]
...     lineup: List[Player]

which ensures that we do not miss a position. Next, we can begin to
express useful statistics through the use of `fmap` and our
unspecified helper methods. For example, given a `game` variable
containing a completed game and a function

>>> def get_player_score(player: Player, inning: Inning) -> int:
...    raise NotImplementedError()

retrieving a player's score during an inning, we can summarize the
contributions of each position in an inning with

>>> from dataclass_applicative import fmap, pure
>>> def half_position_scores(half: Half) -> Positions[int]:
...     return fmap(get_player_score, half.field, pure(half.inning_number))

This is far less tedious than the manual alternative, which might look
like

>>> def half_position_scores(half: Half) -> Dict[Position, int]:
...     return {
...         position: get_player_score(half.field[position], half.inning_number)
...         for position in Position
...     }

with our original `Half` definition.

If we were to fully embrace this style, we might consider re-writing
our `Inning` definition to

>>> @dataclass
... class Inning(Generic[T]):
...     top: T
...     bottom: T

This would allow us write

>>> def inning_position_scores(inning: Inning[Half]) -> Inning[Positions[int]]:
...     return fmap(half_position_scores, inning)

and so on.

.. rubric:: Footnotes

.. [#f1] We are modeling games in which there is a designated
         hitter. In reality we would likely want two definitions of
         the `Positions` class, one with and one without a DH, since
         within a single game only one such `Positions` would be used.
