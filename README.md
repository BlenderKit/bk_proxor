# bk_proxor

Lightweight **PRX** ("Proxor") file format reader/writer and DCC draw
helpers, shared across the [Blendkit](https://www.blendkit.com/) plugin
family (`bk_maya`, `bk_unreal`, and the Blender add-on itself).

A `.prx`/`.prxc` file is a compact preview representation of a BlenderKit
model asset - a wireframe polyline outline plus an optional low-poly hologram
mesh - used to show a live 3D placement preview *before* the full asset has
been downloaded.

## Why this exists

Downloading and importing a full asset can take a while. Drag-and-drop
placement in every host application needs an instant, lightweight stand-in
for the real geometry so users can position, rotate, and preview an asset
while the full download happens in the background. `bk_proxor` is that
stand-in: a tiny, dependency-free format plus per-host conversion helpers.

## Package layout

```
src/bk_proxor/
├── prx_format.py   # DCC-agnostic .prx/.prxc reader & writer (no bpy/maya/unreal imports)
├── _blender/       # Blender: GPU draw pipeline + mesh sampler/generator
├── _maya/          # Maya: PRX -> MUIDrawManager line-segment conversion
└── _unreal/        # Unreal: PRX -> world-space line/mesh vertex conversion
```

`import bk_proxor` only ever imports `prx_format` - the DCC-specific
subpackages (`_blender`, `_maya`, `_unreal`) are imported lazily by each host
plugin, so a missing host dependency (e.g. no `bpy`) in one DCC never breaks
another.

## File format

- **`.prx`** - human-readable text format (line-based, `# PROXOR_VERSION`
  header) for authoring/debugging.
- **`.prxc`** - compact quantized binary format (`PRXQ2` magic, gzip+base64
  payload) used for production asset caching.

Both encode the same data: a bounding box, an optional polyline outline
(`data.line.pos`), and an optional low-poly mesh (`data.mesh.pos` /
`data.mesh.nrm`).

## Usage

```python
from bk_proxor import prx_format

payload = prx_format.read_prx("asset.prxc")
```

Each host then converts the payload into its own coordinate system and draw
API, e.g. for Unreal:

```python
from bk_proxor._unreal.draw import prx_to_line_segments, prx_to_mesh_triangles

lines = prx_to_line_segments(payload, world_scale=100.0)   # metres -> cm
verts = prx_to_mesh_triangles(payload, world_scale=100.0)
```

## Development

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pydoclint .
bandit -r .
```

## Related projects

- [bk_maya](https://github.com/BlenderKit/bk_maya) - Blendkit for Maya
- [bk_unreal](https://github.com/BlenderKit/bk_unreal) - Blendkit for Unreal Engine
- [blenderkit_addon](https://github.com/BlenderKit/blenderkit_addon) - Blendkit for Blender
