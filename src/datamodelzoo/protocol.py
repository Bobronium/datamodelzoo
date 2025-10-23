from __future__ import annotations

from datamodelzoo import Case

# ----------------------------- Protocol classes -----------------------------


class ProtoDeepCopy:
    def __init__(self, xs) -> None:
        self.xs = xs

    def __deepcopy__(self, memo=None):
        import copy

        cls = type(self)
        return cls(copy.deepcopy(self.xs, memo))

    def __eq__(self, other):  # pragma: no cover (equality helper)
        return isinstance(other, ProtoDeepCopy) and self.xs == other.xs


class ProtoDeepCopyMemo:
    def __deepcopy__(self, memo=None):
        if id(self) in memo:
            return memo[id(self)]
        return ProtoDeepCopyMemo()


class ProtoGetNewArgs(int):
    def __new__(cls, payload):
        self = int.__new__(cls, 7)
        self.payload = payload
        return self

    def __getnewargs__(self):
        return (self.payload,)


class ProtoGetNewArgsEx(int):
    def __new__(cls, *, data):
        self = int.__new__(cls, 9)
        self.data = data
        return self

    def __getnewargs_ex__(self):
        return (), {"data": self.data}


class ProtoReduce:
    def __init__(self, a, b) -> None:
        self.a, self.b = a, b

    def __reduce__(self):
        def _rebuild(a, b):
            obj = ProtoReduce.__new__(ProtoReduce)
            obj.a, obj.b = a, b
            return obj

        return (_rebuild, (self.a, self.b))


class ProtoGetStateSetState:
    def __init__(self, foo) -> None:
        self.foo = foo

    def __getstate__(self):
        return {"foo": self.foo}

    def __setstate__(self, st):
        self.__dict__.update(st)


class SlotClass:
    __slots__ = ("a", "b")

    def __init__(self, a, b) -> None:
        self.a, self.b = a, b

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return isinstance(other, SlotClass) and (self.a, self.b) == (other.a, other.b)


# ----------------------------- PROTOCOL OBJECTS -----------------------------

PROTOCOL_OBJECTS: tuple[Case, ...] = (
    Case("proto:__deepcopy__", ProtoDeepCopy(list((1, list((2, 3)))))),
    Case("proto:__deepcopy__(memo=None)", ProtoDeepCopyMemo()),
    Case("proto:__deepcopy__(memo)", [reference := ProtoDeepCopyMemo(), reference]),
    Case("proto:__getnewargs__", ProtoGetNewArgs(list((1, 2, 3)))),
    Case("proto:__getnewargs_ex__", ProtoGetNewArgsEx(data={"k": list((1, 2))})),
    Case("proto:__reduce__", ProtoReduce(a=list((1, 2)), b={"k": list((3,))})),
    Case("proto:getstate_setstate", ProtoGetStateSetState(list((42,)))),
    Case("proto:slots_class", SlotClass(list((1, 2)), {"k": list((3,))})),
)
