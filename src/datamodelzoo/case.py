from __future__ import annotations

import dataclasses as dc
import sys
import types
from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Literal, TypeVar


@dataclass(frozen=True)
class Meta:
    """
    Optional, derived-at-access metadata about a case's underlying object.
    - module: the __module__ of the constructed value's type
    - qualname: the qualified name of the type (if available)
    - text: a short repr(value) preview, bounded to keep catalogs readable
    - purpose: echoes Case.purpose to aid UIs
    """

    module: str | None
    qualname: str | None
    text: str
    purpose: Literal["correctness", "performance", "both"]


TLoader = Callable[[], Any]


@dataclass
class Case:
    name: str
    _obj: Any = None
    factory: TLoader = None
    purpose: Literal["correctness", "performance", "both"] = "both"
    cache: Literal["cache", "rebuild"] = "cache"

    # Internal cache for lazy construction
    _materialized: bool = dc.field(default=False, init=False, repr=False)
    _cache_value: Any = dc.field(default=None, init=False, repr=False)

    def as_pytest_param(self):
        import pytest

        return pytest.param(self, id=self.name)

    @cached_property
    def keywords(self):
        return (keywords := set(self.name.split(":"))) | set(
            sub_keyword for keywords in keywords for sub_keyword in keywords.split("_")
        )

    def _build(self) -> Any:
        if self.factory is not None:
            return self.factory()
        return self._obj

    @property
    def obj(self) -> Any:
        """
        Lazily construct the object. If cache policy is "cache", retain it.
        If cache policy is "rebuild", rebuild on every access.
        """
        if self._obj is not None:
            return self._obj
        if self.cache == "rebuild":
            return self._build()
        self._obj = self._build()
        return self._obj

    @property
    def meta(self) -> Meta:
        """
        Compute lightweight metadata for discovery/debug UIs. May construct the value.
        If constructing is undesirable, consumers should avoid touching .meta and rely on purpose/IDs only.
        """
        val = self.obj
        try:
            tp = type(val)
            module = getattr(tp, "__module__", None)
            qualname = getattr(tp, "__qualname__", getattr(tp, "__name__", None))
        except Exception:  # pragma: no cover
            module, qualname = None, None
        try:
            text = repr(val)
            if len(text) > 120:
                text = text[:117] + "..."
        except Exception:  # pragma: no cover
            text = "<unreprable>"
        return Meta(module=module, qualname=qualname, text=text, purpose=self.purpose)


T = TypeVar("T", bound=types.FunctionType | type[Any])


def make_global(obj: T) -> T:
    """
    Ensure class definitions nested in functions are made importable/pickleable
    by giving them a top-level qualname and binding them in module globals.
    """
    new_qualname = obj.__qualname__.replace("<locals>.", "")
    *parents, name = new_qualname.split(".")
    obj.__name__ = obj.__qualname__ = "_".join(parents) + "_" + name
    sys.modules[obj.__module__].__dict__[obj.__name__] = obj
    return obj
