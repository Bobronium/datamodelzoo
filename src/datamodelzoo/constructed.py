from __future__ import annotations

from typing import Any

from datamodelzoo import Case

# ----------------------------- Helper/engineered types -----------------------------


class MutableKey:
    def __init__(self, _hash=None) -> None:
        self._hash = _hash or 1000

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._hash == other._hash

    def __repr__(self) -> str:
        return f"MutableKey({self._hash!r})"

    def __deepcopy__(self, memo):
        return MutableKey("copied")

    def __hash__(self):
        return hash(self._hash)


def _alias_shared_list_pair():
    shared = ["A", "B"]
    return [shared, shared]


def _alias_mixed_combo():
    shared = ["X", {"k": [1, 2]}]
    return [shared, {"again": shared}, (shared,)]


def _bound_method_holder():
    class ClassWithBoundMethod:
        def m(self) -> int:
            return 1

    inst = ClassWithBoundMethod()
    inst.bound = inst.m  # attribute holding a bound method
    return inst


class DeepcopyRuntimeError:
    """
    A value that mutates its host when deep-copied.
    """

    def __init__(self, host: dict) -> None:
        self._host = host

    def __deepcopy__(self, memo: dict):
        self._host[f"__added_during_iteration_{len(self._host)}__"] = "added during iteration"
        return self


def build_mutating_dict() -> dict:
    """
    Returns a dict where deepcopy of the 'trigger' value will insert a new key
    *iff* 'go_event' is set. The test controls exactly when to flip it.
    """
    host: dict[Any, Any] = {}
    host["trigger"] = DeepcopyRuntimeError(host)
    host["payload"] = {"x": [1, 2, 3]}
    return host


# ----------------------------- CONSTRUCTED OBJECTS -----------------------------

CONSTRUCTED_OBJECTS: tuple[Case, ...] = (
    Case("container:dict_mutable_key", {MutableKey("original"): 42}),
    Case("alias:list_shared_pair", _alias_shared_list_pair()),
    Case("alias:mixed_shared_combo", _alias_mixed_combo()),
    Case("func:bound_method_attr", _bound_method_holder()),
    Case("deepcopy:mutating_dict", build_mutating_dict),
)
