---
name: cad
description: Design 3D CAD models parametrically with CadQuery and export to STEP / STL / OBJ / AMF / SVG / DXF. Use for any mechanical part, enclosure, bracket, gear, or parametric design task.
---

# CAD Skill

## Overview
Build parametric 3D CAD models with **CadQuery** (Python-native CAD).
- Pure Python — no GUI required.
- Exports: STEP (engineering), STL (3D print), OBJ, AMF, SVG (2D drawing), DXF.
- Output path: `/home/z/my-project/download/cad/<part-name>.<ext>`

## Required Library
```bash
pip install cadquery
```
CadQuery bundles `cadquery_ocp` (OpenCascade Python bindings) — large install
(~700MB) but no separate system deps needed.

## Bundled Helper Module
**`skill/cad/scripts/cad_helpers.py`** (stdlib + cadquery):
- `EXPORTERS` — supported format names + extensions + use cases.
- `PARAMS` — common engineering parameters (tolerances, thread specs).
- `MATERIALS` — common materials with density (for mass property calcs).
- `export(result, name, formats, out_dir)` — multi-format export in one call.
- `bbox_summary(result)` — bounding box dimensions as a string.
- `mass_estimate(result, material)` — rough mass from volume × density.
- `save_script(script_text, name)` — persist a parametric script for re-runs.
- `build_plate(parts)` — arrange multiple parts on a cutting plate.

```python
import sys; sys.path.insert(0, "skill/cad/scripts")
from cad_helpers import (EXPORTERS, PARAMS, MATERIALS, export, bbox_summary,
                          mass_estimate, save_script, build_plate)
```
Run `python skill/cad/scripts/cad_helpers.py` to emit a sample bracket +
plate with multi-format exports.

## CadQuery Crash Course

### Workplane (the starting point)
```python
import cadquery as cq

# Start a workplane on the XY plane, centered at origin
result = cq.Workplane("XY").box(10, 10, 3)
```

### Common primitives
```python
# Box
result = cq.Workplane("XY").box(L, W, H)

# Cylinder
result = cq.Workplane("XY").circle(R).extrude(H)

# Sphere
result = cq.Workplane("XY").sphere(R)

# Extrude from a 2D sketch
result = (cq.Workplane("XY")
          .moveTo(0, 0).lineTo(10, 0).lineTo(10, 5).lineTo(0, 5).close()
          .extrude(3))
```

### Holes & pockets
```python
# Through hole on top face
result = (cq.Workplane("XY").box(20, 20, 5)
          .faces(">Z").workplane().hole(3))

# Counterbore
result = (cq.Workplane("XY").box(20, 20, 5)
          .faces(">Z").workplane()
          .cboreHole(3, 6, 2))   # bore_dia, cbore_dia, cbore_depth

# Countersink
result = (cq.Workplane("XY").box(20, 20, 5)
          .faces(">Z").workplane()
          .cskHole(3, 8, 60))    # bore_dia, csk_dia, csk_angle_deg

# Pocket (rectangular)
result = (cq.Workplane("XY").box(20, 20, 5)
          .faces(">Z").workplane()
          .rect(10, 8).cutBlind(-2))
```

### Fillets & chamfers
```python
# Fillet all edges
result = (cq.Workplane("XY").box(20, 20, 5)
          .edges().fillet(1.0))

# Fillet only Z-axis edges
result = (cq.Workplane("XY").box(20, 20, 5)
          .edges("|Z").fillet(1.0))

# Chamfer top edges
result = (cq.Workplane("XY").box(20, 20, 5)
          .edges(">Z").chamfer(0.5))
```

### Boolean operations
```python
box = cq.Workplane("XY").box(20, 20, 5)
cyl = cq.Workplane("XY").circle(3).extrude(5)

# Union
result = box.union(cyl)
# Subtract (cut)
result = box.cut(cyl)
# Intersect
result = box.intersect(cyl)
```

### Selectors (the CadQuery superpower)
```python
.faces(">Z")           # top face (max Z)
.faces("<Z")           # bottom face
.faces("|Z")           # faces parallel to Z axis (side faces)
.edges(">X")           # rightmost edge
.edges("|Y")           # edges parallel to Y
.vertices(">Z and >X") # top-right vertex
.faces("%Plane")       # planar faces only
.edges("%Circle")      # circular edges
```

### Patterns (polar & linear)
```python
# 6 holes around a circle
result = (cq.Workplane("XY").box(50, 50, 5)
          .faces(">Z").workplane()
          .polarArray(15, 0, 360, 6)
          .hole(3))

# 4 holes in a 2x2 grid
result = (cq.Workplane("XY").box(50, 50, 5)
          .faces(">Z").workplane()
          .rarray(30, 30, 2, 2)
          .hole(3))
```

### Loft & sweep
```python
# Loft between two profiles
result = (cq.Workplane("XY").circle(10)
          .workplane(offset=5).rect(8, 8)
          .loft(combine=True))

# Sweep along a path
path = cq.Workplane("XZ").moveTo(0, 0).lineTo(0, 20).lineTo(10, 20)
result = (cq.Workplane("XY").circle(2).sweep(path))
```

## Workflow

1. **Clarify** the part: purpose, dimensions, material, manufacturing process (3D print / CNC / laser cut), tolerances.
2. **Sketch** the parametric plan: what's the driving dimension? What's variable?
3. **Build** the model in a parametric script — every magic number is a named variable.
4. **Export** to STEP (engineering) + STL (3D print) via `export(result, name, ['step','stl'])`.
5. **Verify** with `bbox_summary()` and `mass_estimate()`.
6. **Save script** to `/home/z/my-project/scripts/cad_<name>.py` for re-runs.

## Output Format

```markdown
# CAD Model — {part name}

## Specification
- Purpose: ...
- Material: ...
- Manufacturing: 3D print / CNC / laser cut
- Tolerances: ...

## Dimensions
- Bounding box: {W} × {D} × {H} mm
- Volume: {V} mm³
- Estimated mass: {m} g (assuming {material}, density {ρ} g/cm³)

## Parametric Script
- Path: /home/z/my-project/scripts/cad_{name}.py
- Driving parameters: ...

## Exported Files
- STEP: /home/z/my-project/download/cad/{name}.step
- STL:  /home/z/my-project/download/cad/{name}.stl
- (SVG / DXF / OBJ if requested)

## Notes
- {any non-obvious design decisions}
```

## Self-Check
- [ ] All dimensions parametric (no magic numbers inlined)?
- [ ] STEP exported (engineering deliverable)?
- [ ] STL exported (3D print deliverable, when applicable)?
- [ ] Bounding box verified against design intent?
- [ ] Mass estimated (sanity check vs. spec)?
- [ ] Script saved for re-runs?
- [ ] Tolerances match manufacturing process?
- [ ] Fillets/chamfers added to sharp edges (CNC safety)?

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Magic numbers everywhere | Top-of-script `PARAMS = {...}` block |
| STL too coarse | Pass `tolerance=0.1` (or `angularTolerance=0.1`) to exporter |
| Units confusion | CadQuery is unitless; pick mm consistently and document it |
| Wrong face selector | Use `.faces(">Z")` (string) not `.faces(top)` |
| Boolean order wrong | `box.cut(cyl)` not `cyl.cut(box)` |
| Fillet fails | Reduce radius; check for non-manifold edges first |
| Counterbore depth wrong | `cboreHole(bore, cbore_dia, cbore_depth)` — depth is just the recess |
| Holes not aligned | Use `.polarArray()` / `.rarray()` not manual coordinates |
| Self-intersection | Build primary body first, subtract secondary last |
