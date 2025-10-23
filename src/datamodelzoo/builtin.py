from __future__ import annotations

import fractions
import math
import types
from decimal import Decimal
from typing import Any

from datamodelzoo import Case

# ----------------------------- Graph builders (alias/reflexive/etc.) -----------------------------


def _reflexive_self_list():
    x: list[Any] = []
    x.append(x)
    return x


def _reflexive_self_dict():
    d: dict[str, Any] = {}
    d["self"] = d
    return d


def _reflexive_mutual_lists():
    a: list[Any] = []
    b: list[Any] = []
    a.append(b)
    b.append(a)
    return a  # (b is reachable via a[0])


def _reflexive_tuple_list():
    t = ([],)
    t[0].append(t)
    return t


def _reflexive_dict_list_cross():
    lst: list[Any] = []
    d: dict[str, Any] = {"l": lst}
    lst.append(d)
    return d


def _alias_deep_shared_with_cycle():
    base: list[Any] = []
    pair = [base, base]
    d = {"a": base, "b": pair}
    base.append(d)  # cycle through base -> d -> base
    return d


def _large_deep_graph(depth: int = 6, leaf_len: int = 64):
    leaf = {"payload": list(range(leaf_len))}
    node = leaf
    for i in range(depth):
        node = {"d": i, "pair": [node, {"wrap": node}]}
    root = {"root": node}
    root["alias1"] = root["root"]
    root["alias2"] = root["root"]["pair"][0]
    return root


def _closure_func():
    cap = [1]

    def inner(y: int) -> int:
        cap.append(y)
        return sum(cap)

    return inner


def _mappingproxy():
    return types.MappingProxyType({"a": [1, 2], "b": {"k": 3}})


# ----------------------------- BUILTIN OBJECTS -----------------------------

BUILTIN_OBJECTS: tuple[Case, ...] = (
    # --- atom ---
    Case("atom:None", None),
    Case("atom:type(None)", type(None)),
    Case("atom:bool:True", True),
    Case("atom:type(True)", bool),
    Case("atom:int:1329227995784915872903807060280344576", 2**120),
    Case("atom:float:3.1415926535", 3.1415926535),
    Case("atom:complex:1j", 1j),
    Case("atom:str:'helloሴ'", "hello\u1234"),
    Case("atom:bytes:b'bytes'", b"bytes"),
    Case("atom:Ellipsis", ...),
    Case("atom:NotImplemented", NotImplemented),
    # --- numeric ---
    Case("numeric:Fraction(355, 113)", fractions.Fraction(355, 113)),
    Case("numeric:Decimal('3.1415926535')", Decimal("3.1415926535")),
    Case(
        "numeric:list((0.0, -0.0, inf, -inf, nan))",
        list((0.0, -0.0, math.inf, -math.inf, math.nan)),
    ),
    # --- container (plain, immutable or no alias) ---
    Case("container:list((1, 2, 3, 43))", [1, 2, 3, 43]),
    Case("container:(1, 2, 3)", (1, 2, 3)),
    Case(
        "container:dict(a=True, 42='answer', (1, 2)='tuple-key')",
        {"a": True, 42: "answer", (1, 2): "tuple-key"},
    ),
    Case("container:set((1, 2, 3))", {3, 2, 1}),
    Case("container:set()", set()),
    Case("container:dict()", {}),
    Case("container:list()", []),
    Case("container:tuple()", ()),
    Case("container:frozenset()", frozenset()),
    Case("container:tuple()", tuple()),
    Case("container:list(None, ...)", [None] * 1000),
    # --- reflexive (true cycles) ---
    Case("reflexive:self_list", _reflexive_self_list),
    Case("reflexive:self_dict", _reflexive_self_dict),
    Case("reflexive:mutual_lists", _reflexive_mutual_lists),
    Case("reflexive:tuple_list", _reflexive_tuple_list),
    Case("reflexive:dict_list_cross", _reflexive_dict_list_cross),
    Case("reflexive:deep_shared_subgraph", _alias_deep_shared_with_cycle),
    # --- func / code / descriptors ---
    Case("func:max", max),
    Case("func:<code>", (lambda: None).__code__),
    Case("func:<function <lambda>>", lambda x, y=3: x + y),
    Case("func:property()", property()),
    Case("closure_func", _closure_func),
    # --- large / perf ---
    Case("large:deep_graph_d6_leaf64", _large_deep_graph(35, 64)),
)
