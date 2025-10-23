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


class ProtoDeepCopyError:
    def __deepcopy__(self, memo=None):
        raise RuntimeError("intentional __deepcopy__ failure")


class ProtoCopy:
    def __init__(self, xs) -> None:
        self.xs = xs

    def __copy__(self):
        # shallow copy that preserves container identity of nested members
        if isinstance(self.xs, list):
            new_xs = self.xs.copy()
        else:
            new_xs = self.xs
        return type(self)(new_xs)

    def __eq__(self, other):  # pragma: no cover
        return isinstance(other, ProtoCopy) and self.xs == other.xs


class ProtoCopyError:
    def __copy__(self):
        raise RuntimeError("intentional __copy__ failure")


class ProtoGetNewArgs(int):
    def __new__(cls, payload):
        self = int.__new__(cls, 7)
        self.payload = payload
        return self

    def __getnewargs__(self):
        return (self.payload,)


class ProtoGetNewArgsError(int):
    def __new__(cls, payload):
        self = int.__new__(cls, 1)
        self.payload = payload
        return self

    def __getnewargs__(self):
        raise RuntimeError("intentional __getnewargs__ failure")


class ProtoGetNewArgsEx(int):
    def __new__(cls, *, data):
        self = int.__new__(cls, 9)
        self.data = data
        return self

    def __getnewargs_ex__(self):
        return (), {"data": self.data}


class ProtoGetNewArgsExError(int):
    def __new__(cls, *, data):
        self = int.__new__(cls, 2)
        self.data = data
        return self

    def __getnewargs_ex__(self):
        raise RuntimeError("intentional __getnewargs_ex__ failure")


class ProtoReduce:
    def __init__(self, a, b) -> None:
        self.a, self.b = a, b

    def __reduce__(self):
        def _rebuild(a, b):
            obj = ProtoReduce.__new__(ProtoReduce)
            obj.a, obj.b = a, b
            return obj

        return (_rebuild, (self.a, self.b))


class ProtoReduceError:
    def __reduce__(self):
        raise RuntimeError("intentional __reduce__ failure")


class ProtoReduceEx:
    def __init__(self, a, b) -> None:
        self.a, self.b = a, b

    def __reduce_ex__(self, protocol: int):
        def _rebuild(a, b):
            obj = ProtoReduceEx.__new__(ProtoReduceEx)
            obj.a, obj.b = a, b
            return obj

        return (_rebuild, (self.a, self.b))


class ProtoReduceExError:
    def __reduce_ex__(self, protocol: int):
        raise RuntimeError("intentional __reduce_ex__ failure")


class ProtoGetStateSetState:
    def __init__(self, foo) -> None:
        self.foo = foo

    def __getstate__(self):
        return {"foo": self.foo}

    def __setstate__(self, st):
        self.__dict__.update(st)


class ProtoGetStateRaises:
    def __init__(self, foo) -> None:
        self.foo = foo

    def __getstate__(self):
        raise RuntimeError("intentional __getstate__ failure")


class ProtoSetStateRaises:
    def __setstate__(self, st):
        raise RuntimeError("intentional __setstate__ failure")


class ProtoGetInitArgs:
    def __init__(self, a, b) -> None:
        self.a, self.b = a, b

    def __getinitargs__(self):
        # for older pickle protocols (0-2)
        return (self.a, self.b)


class ProtoGetInitArgsError:
    def __getinitargs__(self):
        raise RuntimeError("intentional __getinitargs__ failure")


class SlotClass:
    __slots__ = ("a", "b")

    def __init__(self, a, b) -> None:
        self.a, self.b = a, b

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return isinstance(other, SlotClass) and (self.a, self.b) == (other.a, other.b)


# ----------------------------- PROTOCOL OBJECTS -----------------------------

PROTOCOL_OBJECTS: tuple[Case, ...] = (
    # deepcopy protocol
    Case("proto:__deepcopy__", ProtoDeepCopy(list((1, list((2, 3)))))),
    Case("proto:__deepcopy__(memo=None)", ProtoDeepCopyMemo()),
    Case("proto:__deepcopy__(memo)", [reference := ProtoDeepCopyMemo(), reference]),
    Case("proto:__deepcopy__ (raises)", ProtoDeepCopyError()),

    # copy protocol
    Case("proto:__copy__", ProtoCopy(list((1, list((2, 3)))))),
    Case("proto:__copy__ (raises)", ProtoCopyError()),

    # __getnewargs__/__getnewargs_ex__
    Case("proto:__getnewargs__", ProtoGetNewArgs(list((1, 2, 3)))),
    Case("proto:__getnewargs__ (raises)", ProtoGetNewArgsError(list((1, 2, 3)))),
    Case("proto:__getnewargs_ex__", ProtoGetNewArgsEx(data={"k": list((1, 2))})),
    Case("proto:__getnewargs_ex__ (raises)", ProtoGetNewArgsExError(data={"k": list((1, 2))})),

    # __reduce__/__reduce_ex__
    Case("proto:__reduce__", ProtoReduce(a=list((1, 2)), b={"k": list((3,))})),
    Case("proto:__reduce__ (raises)", ProtoReduceError()),
    Case("proto:__reduce_ex__", ProtoReduceEx(a=list((1, 2)), b={"k": list((3,))})),
    Case("proto:__reduce_ex__ (raises)", ProtoReduceExError()),

    # __getstate__/__setstate__
    Case("proto:getstate_setstate", ProtoGetStateSetState(list((42,)))),
    Case("proto:getstate_setstate (raises in getstate)", ProtoGetStateRaises(list((42,)))),
    Case("proto:getstate_setstate (raises in setstate)", ProtoSetStateRaises()),

    # __getinitargs__
    Case("proto:__getinitargs__", ProtoGetInitArgs(list((1, 2)), {"k": list((3,))})),
    Case("proto:__getinitargs__ (raises)", ProtoGetInitArgsError()),

    # slots
    Case("proto:slots_class", SlotClass(list((1, 2)), {"k": list((3,))})),
)
