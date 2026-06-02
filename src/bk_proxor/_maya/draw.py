"""Pure-data conversion: PRX payload -> list of Maya line segments.

Maya's ``MUIDrawManager.line()`` consumes pairs of ``MPoint``; this helper
turns the PRX ``data['line']['pos']`` array (flat list of consecutive
endpoint pairs, Blender Z-up, meters) into a list of
``[(ax, ay, az), (bx, by, bz)]`` segments in Maya world coords (Y-up,
internal units — typically centimetres).

The conversion is intentionally framework-agnostic so callers can build
``MPoint`` objects themselves and avoid pulling Maya imports into this
module.
"""

from __future__ import annotations

from typing import Any


# Blender Z-up metres -> Maya Y-up centimetres.
# Caller can override ``world_scale`` (default 100.0) if their host uses
# a different internal unit.
_DEFAULT_SCALE = 100.0


def prx_to_line_segments(
    payload: dict[str, Any],
    *,
    world_scale: float = _DEFAULT_SCALE,
    axis_swap_yz: bool = True,
) -> list[list[tuple[float, float, float]]]:
    """Return a list of ``[(ax,ay,az), (bx,by,bz)]`` segments.

    Args:
        payload: A parsed PRX dict (as returned by ``prx_format.read_prx``).
                 Either the full ``{"data": {...}}`` wrapper or the inner
                 data dict is accepted.
        world_scale: Multiplier applied to every coordinate. Default
                     ``100.0`` converts metres to Maya centimetres.
        axis_swap_yz: When ``True`` swaps Y and Z so a Blender Z-up source
                      becomes Y-up. Set ``False`` if the host coord system
                      already matches the PRX source.

    Returns:
        Possibly-empty list of two-point segments suitable for direct
        consumption by ``MUIDrawManager.line()`` in a Maya draw override.
    """
    if not isinstance(payload, dict):
        return []

    data = payload.get("data", payload)
    if not isinstance(data, dict):
        return []

    positions = (data.get("line") or {}).get("pos") or []
    segments: list[list[tuple[float, float, float]]] = []

    # PRX stores polylines as flat pairs: [a0, b0, a1, b1, ...].
    for i in range(0, len(positions) - 1, 2):
        try:
            ax, ay, az = (float(v) for v in positions[i][:3])
            bx, by, bz = (float(v) for v in positions[i + 1][:3])
        except (TypeError, ValueError, IndexError):
            continue

        if axis_swap_yz:
            a = (ax * world_scale, az * world_scale, ay * world_scale)
            b = (bx * world_scale, bz * world_scale, by * world_scale)
        else:
            a = (ax * world_scale, ay * world_scale, az * world_scale)
            b = (bx * world_scale, by * world_scale, bz * world_scale)

        segments.append([a, b])

    return segments
