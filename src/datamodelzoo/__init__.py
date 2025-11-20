__version__ = "0.1.0"

from datamodelzoo.case import Case

__all__ = ["EVIL_CASES", "CASES", "Case", "__version__"]

import os
from typing import Literal

from datamodelzoo.builtin import BUILTIN_OBJECTS
from datamodelzoo.constructed import CONSTRUCTED_OBJECTS
from datamodelzoo.protocol import PROTOCOL_OBJECTS
from datamodelzoo.special import SPECIAL_OBJECTS
from datamodelzoo.stdlib import STDLIB_OBJECTS
from datamodelzoo.thirdparty import thirdparty_cases
from datamodelzoo.evil import EVIL_CASES

CASES: tuple[Case, ...] = (
    BUILTIN_OBJECTS
    + PROTOCOL_OBJECTS
    + STDLIB_OBJECTS
    + SPECIAL_OBJECTS
    + CONSTRUCTED_OBJECTS
    + thirdparty_cases()
)


Purpose = Literal["correctness", "performance", "both"]
