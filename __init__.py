"""Dev shim that makes the ``bk_proxor`` git submodule import-compatible.

Two on-disk layouts exist for the same package:

* **Packaged addon** - ``dev.py`` copies ``bk_proxor/src/bk_proxor`` to
  ``<addon>/bk_proxor``, so ``bk_proxor`` is a normal flat package and *this*
  file is not shipped at all (it is replaced by the inner package ``__init__``).
* **Hardlinked dev checkout** - the whole repo is linked as-is, so
  ``<addon>/bk_proxor`` is this submodule root and the real package lives one
  level down under ``src/bk_proxor``.

To keep the exact same relative imports working in both layouts (e.g.
``from .bk_proxor._blender import draw`` and ``from .bk_proxor import
prx_format``), we point this package's ``__path__`` at the inner
``src/bk_proxor`` directory when it exists. Submodules (``prx_format``,
``_blender``, ``_maya``) are then resolved from there, so nothing needs to know
about the ``src/`` nesting.
"""

from __future__ import annotations

import os

_INNER_PKG = os.path.join(os.path.dirname(__file__), "src", "bk_proxor")
if os.path.isdir(_INNER_PKG):
    # Redirect submodule resolution to the real src-layout package.
    __path__ = [_INNER_PKG]

# Re-export the DCC-agnostic format I/O so ``bk_proxor.prx_format`` resolves
# regardless of layout. Imported after the __path__ redirect so it is found in
# the inner package during dev.
from . import prx_format  # noqa: E402,F401

__all__ = ["prx_format"]
