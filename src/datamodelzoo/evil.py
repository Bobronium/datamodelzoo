from __future__ import annotations

import uuid
from typing import Any, Iterator

import copyreg

from datamodelzoo import Case


class EvilEx(Exception):
    pass


class EvilDeepCopy:
    def __deepcopy__(self, memo) -> Any:
        raise EvilEx()


class EvilDeepCopyNoMemoArg:
    def __deepcopy__(self) -> Any:
        raise AssertionError(
            f"this must never be executed {uuid.uuid4()} due to __deepcopy__ not accepting memo arg"
        )


class EvilReduceArgs:
    def __reduce__(self) -> Any:
        return EvilReduceArgs, "not-a-tuple-of-args"


class EvilReduceRaises:
    def __reduce__(self) -> Any:
        raise EvilEx("__reduce__ exploded for bad tuple case")


class EvilReduceCallable:
    def __reduce__(self) -> Any:
        return 42, ()


class EvilStateSlotsMapping:
    """
    Mapping-like object used as slot_state in reduce state.

    It deliberately raises when the copier tries to pull values via
    __getitem__ while iterating keys from __iter__.
    """

    def __iter__(self) -> Iterator[str]:
        # A single bogus slot name.
        yield "slot_attr"

    def __getitem__(self, key: str) -> Any:
        raise EvilEx("slot_state.__getitem__ exploded for key {!r}".format(key))


class EvilHasSlotsState:
    """
    Object whose reduce() returns a (dict_state, slot_state) pair, where the
    slot_state misbehaves via __iter__/__getitem__.
    """

    def __reduce__(self) -> Any:
        # No-arg constructor with state split into dict_state and slot_state.
        dict_state = {"foo": 10}
        slot_state = EvilStateSlotsMapping()
        state = (dict_state, slot_state)
        return self.__class__, (), state


class EvilHasSlotsStateSlotOnly:
    """
    Variant of EvilHasSlotsState whose reduce() state is (None, slot_state).

    For this shape, stdlib copy.deepcopy will skip any __dict__ update and go
    straight to the slot_state mapping, so the first observable failure is
    the slot_state.__getitem__ EvilEx rather than an AttributeError about
    missing __dict__. copium's deepcopy is aligned to that behavior.
    """

    def __reduce__(self) -> Any:
        # dict_state is explicitly None so that copy._reconstruct does not try
        # y.__dict__.update(dict_state) before consulting slot_state.
        dict_state = None
        slot_state = EvilStateSlotsMapping()
        state = (dict_state, slot_state)
        return self.__class__, (), state


class EvilSetStateRaisesOnSecondItem:
    """
    Object whose __setstate__ mutates internal state and then raises.

    This is meant to stress the shallow-copy state application path
    (reconstruct_state in _copying.c).
    """

    def __getstate__(self) -> Any:
        return {"values": [1, 2, 3]}

    def __setstate__(self, state: Any) -> None:
        raise EvilEx("boom inside __setstate__")


class EvilDictIterBadPairs:
    """Iterator used as dictiter that yields invalid (k, v) pairs."""

    def items(self) -> "EvilDictIterBadPairs":
        return self

    def __iter__(self) -> "EvilDictIterBadPairs":
        # Make this a proper iterator so the dictiter path is actually hit.
        return self

    def __next__(self) -> Any:
        # Yield a single 1-element tuple, then stop.
        if getattr(self, "_done", False):
            raise StopIteration
        self._done = True  # type: ignore[attr-defined]
        return ("only-key",)


class EvilUsesDictIter:
    """
    Object whose __reduce__ uses a dictiter whose elements are structurally
    wrong (not 2-tuples), to exercise the dictiter handling path.
    """

    def __reduce__(self) -> Any:
        # constructor, args, state=None, listiter=None, dictiter=EvilDictIterBadPairs()
        return self.__class__, (), None, None, EvilDictIterBadPairs()


class EvilViaCopyreg:
    """
    Type that is registered in copyreg.dispatch_table so deepcopy/copy
    uses the registry reducer rather than __reduce__ directly.
    """

    pass


class EvilViaCopyregRaises:
    """
    Variant of EvilViaCopyreg whose registered reducer raises EvilEx.
    """

    pass


def _evil_registry_reduce(obj: EvilViaCopyreg) -> Any:
    # Return something that is *formally* a tuple but semantically bogus:
    # wrong length and wrong types.
    return ("not-a-callable",)


def _evil_registry_reduce_raises(obj: EvilViaCopyregRaises) -> Any:
    # Reducer that always raises EvilEx when invoked.
    raise EvilEx("copyreg reducer exploded for EvilViaCopyregRaises")


# Register the evil reducer with copyreg so that try_reduce_via_registry()
# will find it for EvilViaCopyreg variants.
copyreg.pickle(EvilViaCopyreg, _evil_registry_reduce)
copyreg.pickle(EvilViaCopyregRaises, _evil_registry_reduce_raises)


# ---------------------------------------------------------------------------
# Descriptor-based evil magic methods
# ---------------------------------------------------------------------------


class RaisingDescriptor:
    """
    Data descriptor that always raises EvilEx when accessed.

    Used to model objects where the *lookup* of a magic method explodes
    before the copier even has a chance to call it.
    """

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        raise EvilEx("descriptor-based access exploded")


class EvilDescriptorDeepCopy:
    """
    Object that exposes __deepcopy__ via a descriptor that raises on access.
    """

    __deepcopy__ = RaisingDescriptor()


class EvilDescriptorReduce:
    """
    Object that exposes __reduce__ via a descriptor that raises on access.
    """

    __reduce__ = RaisingDescriptor()


class EvilDescriptorReduceEx:
    """
    Object that exposes __reduce_ex__ via a descriptor that raises on access.
    """

    __reduce_ex__ = RaisingDescriptor()


class EvilDescriptorGetstate:
    """
    Object that exposes __getstate__ via a descriptor that raises on access.
    """

    __getstate__ = RaisingDescriptor()


class EvilDescriptorSetstate:
    """
    Object that exposes __setstate__ via a descriptor that raises on access.

    Note: __getstate__ is provided so that reconstruction actually has
    a non-None state, forcing the copying logic to look up __setstate__
    and thus hit the descriptor.
    """

    __setstate__ = RaisingDescriptor()

    def __getstate__(self) -> Any:
        # Any non-None dummy state is enough.
        return {"dummy": True}


# ---------------------------------------------------------------------------
# Helper: build individual Case instances for all container types
# ---------------------------------------------------------------------------


def _wrap_in_containers(name: str, obj: Any) -> tuple[Case, ...]:
    """
    Return a sequence of Case instances that place `obj` into:
      - the bare object
      - list
      - tuple
      - dict (as value and as key, in separate cases)
      - set
      - frozenset

    This ensures that container-specialised code paths (list/tuple/dict/set/
    frozenset) each see the object under their own dedicated Case.
    """
    cases: list[Case] = []

    cases.extend(
        (
            Case(f"{name}", obj),
            Case(f"{name}:nested-in-list", [obj, [obj]]),
            Case(f"{name}:nested-in-tuple", (obj, (obj,))),
            Case(f"{name}:nested-as-dict-value", {"as_value": obj}),
            Case(f"{name}:nested-as-dict-key", {obj: "as_key"}),
            Case(f"{name}:nested-in-set", {obj}),
            Case(f"{name}:nested-in-frozenset", frozenset({obj})),
        )
    )

    return tuple(cases)


_deepcopy_cases = _wrap_in_containers(
    "evil:__deepcopy__",
    EvilDeepCopy(),
)

_deepcopy_no_memo_cases = _wrap_in_containers(
    "evil:__deepcopy__-no-memo-arg",
    EvilDeepCopyNoMemoArg(),
)

_reduce_args_cases = _wrap_in_containers(
    "evil:__reduce__:args-not-tuple",
    EvilReduceArgs(),
)

_reduce_bad_tuple_raises_cases = _wrap_in_containers(
    "evil:__reduce__:raises",
    EvilReduceRaises(),
)

_reduce_non_callable_cases = _wrap_in_containers(
    "evil:__reduce__:non-callable-constructor",
    EvilReduceCallable(),
)

_copyreg_evil_cases = _wrap_in_containers(
    "evil:copyreg-registered-reducer-is-bogus",
    EvilViaCopyreg(),
)

_copyreg_evil_raises_cases = _wrap_in_containers(
    "evil:copyreg-registered-reducer-raises",
    EvilViaCopyregRaises(),
)

# Slot/state / dictiter based misbehaviour also go through the container
# matrix, so their payloads appear bare and inside each container type.

_slots_state_cases = _wrap_in_containers(
    "evil:slot_state-mapping-misbehaves",
    EvilHasSlotsState(),
)

_slots_state_slotonly_cases = _wrap_in_containers(
    "evil:slot_state-mapping-misbehaves-slot-only",
    EvilHasSlotsStateSlotOnly(),
)

_setstate_raises_cases = _wrap_in_containers(
    "evil:__setstate__-raises-after-partial-update",
    EvilSetStateRaisesOnSecondItem(),
)

_dictiter_bad_pairs_cases = _wrap_in_containers(
    "evil:dictiter-yields-invalid-pairs",
    EvilUsesDictIter(),
)

# Descriptor-based magic methods that explode on attribute access

_descriptor_deepcopy_cases = _wrap_in_containers(
    "evil:descriptor-__deepcopy__",
    EvilDescriptorDeepCopy(),
)

_descriptor_reduce_cases = _wrap_in_containers(
    "evil:descriptor-__reduce__",
    EvilDescriptorReduce(),
)

_descriptor_reduce_ex_cases = _wrap_in_containers(
    "evil:descriptor-__reduce_ex__",
    EvilDescriptorReduceEx(),
)

_descriptor_getstate_cases = _wrap_in_containers(
    "evil:descriptor-__getstate__",
    EvilDescriptorGetstate(),
)

_descriptor_setstate_cases = _wrap_in_containers(
    "evil:descriptor-__setstate__",
    EvilDescriptorSetstate(),
)

EVIL_CASES: tuple[Case, ...] = (
    # Bad __reduce__ tuples
    *_reduce_args_cases,
    *_reduce_bad_tuple_raises_cases,
    *_reduce_non_callable_cases,
    # __deepcopy__ misbehaviour
    *_deepcopy_cases,
    *_deepcopy_no_memo_cases,
    # copyreg dispatch-table reducer that returns invalid shape or raises
    *_copyreg_evil_cases,
    *_copyreg_evil_raises_cases,
    # Slot-state and __setstate__ misbehaviour, plus dictiter weirdness,
    # all fully fanned out across the container specialisations.
    *_slots_state_cases,
    *_slots_state_slotonly_cases,
    *_setstate_raises_cases,
    *_dictiter_bad_pairs_cases,
    # Descriptor-based magic methods that explode on attribute access
    *_descriptor_deepcopy_cases,
    *_descriptor_reduce_cases,
    *_descriptor_reduce_ex_cases,
    *_descriptor_getstate_cases,
    *_descriptor_setstate_cases,
)