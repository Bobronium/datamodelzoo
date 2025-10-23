from __future__ import annotations

from dataclasses import dataclass

from datamodelzoo import Case


@dataclass
class A:
    a: list
    b: str
    c: bool


@dataclass
class ASmall:
    a: int


SPECIAL_OBJECTS: tuple[Case, ...] = (
    Case(
        "cpython:91610:dict",
        {"list": [1, 2, 3, 43], "t": (1, 2, 3), "str": "hello", "subdict": {"a": True}},
    ),
    Case("cpython:91610:dataclass", A([1, 2, 3], "hello", True)),
    Case("cpython:91610:dataclass_small", ASmall(123)),
    Case("cpython:91610:small_tuple", (1,)),
    Case("cpython:91610:repeating", [ASmall(123)] * 100),
    Case("cpython:91610:repeating_atomic", [[1] * 100]),
)
