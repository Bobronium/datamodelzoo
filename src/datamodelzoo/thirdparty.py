from __future__ import annotations

from typing import Any, TypeVar

from datamodelzoo import Case
from datamodelzoo.case import make_global

T = TypeVar("T", bound=type[Any] | Any)


def thirdparty_cases() -> tuple[Case, ...]:
    """
    Return Case declarations with *lazy loaders*.
    Heavy imports happen inside each loader, not at catalog build time.
    This ensures case IDs are visible without constructing the objects or importing big deps.
    """
    out: list[Case] = []

    # ----- numpy -----
    def _np_array_i32_2x3():
        import numpy as np

        return np.arange(6, dtype=np.int32).reshape(2, 3)

    def _np_array_f64_nan_inf():
        import numpy as np

        return np.array([0.0, -0.0, np.nan, np.inf, -np.inf])

    def _np_array_structured():
        import numpy as np

        return np.array([(1, 2.0), (3, 4.5)], dtype=[("a", "i4"), ("b", "f8")])

    def _np_object_alias_array():
        import numpy as np

        shared = {"k": [1, 2]}
        arr = np.empty(3, dtype=object)
        arr[:] = [shared, shared, shared]
        return arr

    out += [
        Case("thirdparty:numpy:array_i32_2x3", factory=_np_array_i32_2x3),
        Case("thirdparty:numpy:array_f64_nan_inf", factory=_np_array_f64_nan_inf),
        Case("thirdparty:numpy:array_structured", factory=_np_array_structured),
        Case("thirdparty:numpy:array_object_alias", factory=_np_object_alias_array),
    ]

    # ----- pandas -----
    def _pd_series_Int64_na():
        import pandas as pd

        return pd.Series([1, None, 3], dtype="Int64")

    def _pd_dataframe_categorical():
        import pandas as pd

        return pd.DataFrame({"a": [1, 2, 1], "b": pd.Categorical(["x", "y", "x"])})

    def _pd_dataframe_dt_tz():
        import pandas as pd

        return pd.DataFrame(
            {"ts": pd.to_datetime(["2025-08-30T12:00:00Z", "2025-08-31T00:00:00Z"])}
        )

    out += [
        Case("thirdparty:pandas:series_Int64_na", factory=_pd_series_Int64_na),
        Case("thirdparty:pandas:dataframe_categorical", factory=_pd_dataframe_categorical),
        Case("thirdparty:pandas:dataframe_dt_tz", factory=_pd_dataframe_dt_tz),
    ]

    # ----- pydantic -----
    def _pydantic_model_with_alias():
        from pydantic import BaseModel, Field

        @make_global
        class UserModel(BaseModel):
            id: int
            name: str = "Alice"
            tags: list[str | dict[str, list[int]]] = Field(default_factory=lambda: ["x"])

        shared = ["tag", {"k": [1, 2]}]
        model = UserModel(id=1, name="Bob", tags=shared)
        return {"model": model, "alias": shared}

    out += [Case("thirdparty:pydantic:basemodel_with_alias", factory=_pydantic_model_with_alias)]

    # ----- attrs -----
    def _attrs_define_instance():
        import attrs

        @make_global
        @attrs.define
        class A:
            x: int
            y: list[int]

        return A(1, [2, 3])

    out += [Case("thirdparty:attrs:define_instance", factory=_attrs_define_instance)]

    # ----- msgspec -----
    def _msgspec_struct_instance():
        import msgspec

        @make_global
        class S(msgspec.Struct):
            x: int
            y: list[int]

        return S(1, [2, 3])

    out += [Case("thirdparty:msgspec:struct_instance", factory=_msgspec_struct_instance)]

    # ----- Pillow -----
    def _pillow_image_rgba_2x2():
        from PIL import Image

        return Image.new("RGBA", (2, 2), (255, 0, 0, 128))

    out += [Case("thirdparty:pillow:image_rgba_2x2", factory=_pillow_image_rgba_2x2)]

    # ----- torch -----
    def _torch_tensor_long_2x3():
        import torch

        return torch.arange(6).reshape(2, 3)

    out += [Case("thirdparty:torch:tensor_long_2x3", factory=_torch_tensor_long_2x3)]

    # ----- sympy -----
    def _sympy_expr_sin2_plus_cos2():
        import sympy as sp

        x = sp.Symbol("x")
        return sp.sin(x) ** 2 + sp.cos(x) ** 2

    out += [Case("thirdparty:sympy:expr_sin2_plus_cos2", factory=_sympy_expr_sin2_plus_cos2)]

    # ----- networkx -----
    def _networkx_digraph_2cycle():
        import networkx as nx

        g = nx.DiGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        return g

    out += [Case("thirdparty:networkx:digraph_2cycle", factory=_networkx_digraph_2cycle)]

    def _get_jsonschema():
        import jsonschema

        return jsonschema

    out.extend(
        (
            Case(
                "thirdparty:jsonschema:Draft202012Validator.META_SCHEMA",
                factory=lambda: _get_jsonschema().Draft202012Validator.META_SCHEMA,
            ),
            Case(
                "thirdparty:jsonschema:Draft7Validator.META_SCHEMA",
                factory=lambda: _get_jsonschema().Draft7Validator.META_SCHEMA,
            ),
        ),
    )
    return tuple(out)
