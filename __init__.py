"""Maya-addon shim around the ``bk_proxor`` git submodule.

The submodule itself follows a standard src-layout:

    bk_maya/bk_proxor/        <- this folder = submodule root
    ├── pyproject.toml
    └── src/
        └── bk_proxor/        <- real importable package
            ├── __init__.py
            ├── prx_format.py
            ├── _blender/...
            └── _maya/...

To keep imports clean for both this addon AND any future DCC host that
vendors the same submodule, we:

1. Add ``<submodule>/src`` to ``sys.path`` so ``import bk_proxor`` Just
   Works anywhere in the addon code, AND
2. Re-export the inner package via *this* module so existing code that
   does ``from bk_maya.bk_proxor import prx_format`` keeps working.
"""

from __future__ import annotations

import os
import sys

_SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
if os.path.isdir(_SRC_DIR) and _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Re-export so ``bk_maya.bk_proxor.prx_format`` resolves without users
# needing to know about the inner ``src/bk_proxor/`` layout.
from bk_proxor import prx_format  # noqa: E402,F401

__all__ = ["prx_format"]
