from __future__ import annotations

import array
import datetime as dt
import enum
import inspect
import re
import traceback
import types
import uuid
from dataclasses import dataclass
from typing import Any, NamedTuple

from datamodelzoo import Case

# ----------------------------- Helper types / factories -----------------------------


class Animal(enum.Enum):
    CAT = 1
    DOG = 2


class Point(NamedTuple):
    x: int
    y: int
    meta: Any = None


@dataclass
class UserDC:
    name: str
    tags: list[str]
    props: dict[str, Any]


@dataclass(frozen=True)
class FrozenPair:
    x: int
    y: tuple[int, ...]


def _make_traceback_exception():
    try:
        1 / 0
    except Exception as e:  # pragma: no cover - deterministic payload
        return traceback.TracebackException.from_exception(e)


# ----------------------------- STDLIB OBJECTS -----------------------------

STDLIB_OBJECTS: tuple[Case, ...] = (
    Case("atom:bytearray:b'ba'", bytearray(b"ba")),
    Case("atom:uuid:uuid4", uuid.UUID("dd203681-c578-4442-995d-4dfff9587372")),
    Case("numeric:array('i', [1, 2, 3, 4])", array.array("i", [1, 2, 3, 4])),
    Case("container:frozenset((1, 2, 3))", frozenset((1, 2, 3))),
    Case("container:slice(1, 10, 2)", slice(1, 10, 2)),
    Case("container:range(5, 50, 5)", range(5, 50, 5)),
    Case("stdlib:FrozenPair(1, (2, 3, 4))", FrozenPair(1, (2, 3, 4))),
    Case("stdlib:Point(1, 2, {'k': [3, 4]})", Point(1, 2, {"k": [3, 4]})),
    Case(
        "stdlib:UserDC('alice', list(('x', 'y')), dict(score=[1, 2, 3]))",
        UserDC("alice", ["x", "y"], {"score": [1, 2, 3]}),
    ),
    Case("stdlib:dict(id=7, name='Alice')", {"id": 7, "name": "Alice"}),
    Case(
        "stdlib:dict(nested)",
        {"list": [1, 2, 3, 43], "t": (1, 2, 3), "str": "hello", "subdict": {"a": True}},
    ),
    Case("stdlib:enum:Animal.CAT", Animal.CAT),
    Case(
        "stdlib:inspect.signature(lambda a, b: (a, b))",
        inspect.signature(lambda a, b: (a, b)),
    ),
    Case(
        "stdlib:re.compile('\\\\w+', flags=IGNORECASE|MULTILINE)",
        re.compile(r"\w+", flags=re.IGNORECASE | re.MULTILINE),
    ),
    Case("stdlib:traceback_exception", _make_traceback_exception()),
    Case(
        "stdlib:types.SimpleNamespace(a=list((1, 2)), b={'k': 3})",
        types.SimpleNamespace(a=[1, 2], b={"k": 3}),
    ),
    Case("time:date:2025-08-30", dt.date(2025, 8, 30)),
    Case("time:datetime:2025-08-30T12:34:56.000789", dt.datetime(2025, 8, 30, 12, 34, 56, 789)),
    Case("time:time:12:34:56.000789", dt.time(12, 34, 56, 789)),
    Case("time:timedelta:3d7s", dt.timedelta(days=3, seconds=7)),
)
