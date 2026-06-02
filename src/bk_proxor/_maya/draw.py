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
# PRX positions are stored as ``raw * 100`` (Blender convention multiplies
# by 0.01 to get metres). Default ``world_scale=100`` then converts those
# metres to Maya's internal centimetres, so the on-disk values pass
# straight through (raw * 0.01 * 100 = raw).
_DEFAULT_SCALE = 100.0
_PRX_TO_METRES = 0.01


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

        s = float(world_scale) * _PRX_TO_METRES
        if axis_swap_yz:
            # Blender Z-up: swap Y/Z; host front-axis matches PRX z so no negation.
            a = (ax * s, az * s, ay * s)
            b = (bx * s, bz * s, by * s)
        else:
            # Maya Y-up: PRX Y is already up, but Blender +Y (back) maps to
            # Maya -Z so the host front-axis is flipped — negate Z.
            a = (ax * s, ay * s, -az * s)
            b = (bx * s, by * s, -bz * s)

        segments.append([a, b])

    return segments


def prx_to_mesh_triangles(
    payload: dict[str, Any],
    *,
    world_scale: float = _DEFAULT_SCALE,
    axis_swap_yz: bool = True,
) -> list[tuple[float, float, float]]:
    """Return mesh vertices as a flat list of ``(x, y, z)`` triples.

    The PRX ``data['mesh']['pos']`` array stores triangle vertices
    consecutively (3 vertices per triangle, no index buffer). Caller
    can chunk the returned list into 3-tuples to get triangles, or
    feed it directly to ``MUIDrawManager.mesh(kTriangles, ...)``.

    Returns an empty list when the payload contains no mesh section.
    """
    if not isinstance(payload, dict):
        return []
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        return []
    positions = (data.get("mesh") or {}).get("pos") or []
    s = float(world_scale) * _PRX_TO_METRES
    out: list[tuple[float, float, float]] = []
    for p in positions:
        try:
            x, y, z = (float(v) for v in p[:3])
        except (TypeError, ValueError, IndexError):
            continue
        if axis_swap_yz:
            out.append((x * s, z * s, y * s))
        else:
            # Maya Y-up: negate Z to match Maya's front-axis (see line helper).
            out.append((x * s, y * s, -z * s))
    # Round triangle count: discard any trailing 1 or 2 dangling verts.
    n_tris = len(out) // 3
    return out[: n_tris * 3]


def prx_to_mesh_normals(
    payload: dict[str, Any],
    *,
    axis_swap_yz: bool = True,
) -> list[tuple[float, float, float]]:
    """Return mesh normals (axis-swapped to match :func:`prx_to_mesh_triangles`).

    Length matches the vertex count of the mesh; pass to
    ``MUIDrawManager.mesh(... normal=MVectorArray)`` for lit rendering.
    """
    if not isinstance(payload, dict):
        return []
    data = payload.get("data", payload)
    if not isinstance(data, dict):
        return []
    normals = (data.get("mesh") or {}).get("nrm") or []
    out: list[tuple[float, float, float]] = []
    for n in normals:
        try:
            x, y, z = (float(v) for v in n[:3])
        except (TypeError, ValueError, IndexError):
            continue
        if axis_swap_yz:
            out.append((x, z, y))
        else:
            out.append((x, y, z))
    return out
