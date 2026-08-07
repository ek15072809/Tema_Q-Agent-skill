"""cad_helpers.py — Helpers for CadQuery-based CAD design and export.

Requires `cadquery` (pip install cadquery). All other imports are stdlib.

Provides:
  * EXPORTERS                — supported format names + extensions + use cases.
  * PARAMS                   — common engineering parameters (tolerances, threads).
  * MATERIALS                — common materials with density (g/cm³).
  * export(result, name, formats, out_dir) — multi-format export.
  * bbox_summary(result)     — bounding box dimensions as a string.
  * mass_estimate(result, material)        — rough mass (g) from volume × density.
  * save_script(script_text, name)         — persist a parametric script.
  * build_plate(parts)                     — arrange multiple parts on a cutting plate.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable


# ---- Supported exporters -------------------------------------------------

EXPORTERS: dict[str, dict] = {
    "step": {"ext": "step", "use": "Engineering / CAM / CNC interchange (lossless B-rep)."},
    "stl":  {"ext": "stl",  "use": "3D printing (mesh; lossy). Use tolerance=0.1 for fine mesh."},
    "obj":  {"ext": "obj",  "use": "3D rendering / game engines (mesh with material groups)."},
    "amf":  {"ext": "amf",  "use": "Additive manufacturing (mesh; richer than STL)."},
    "svg":  {"ext": "svg",  "use": "2D drawing / technical illustration of the model."},
    "dxf":  {"ext": "dxf",  "use": "2D CAD interchange (laser cutting, waterjet)."},
    "gltf": {"ext": "glb",  "use": "Web 3D viewer / AR / VR."},
}


# ---- Engineering parameters ----------------------------------------------

PARAMS: dict[str, dict] = {
    "tolerance": {
        "3d_print_fdm":   0.3,   # mm — FDM layer ~0.2-0.3
        "3d_print_sla":   0.1,   # mm — SLA is finer
        "cnc_mill":       0.05,  # mm — typical CNC
        "laser_cut":      0.1,   # mm — kerf compensation
    },
    "clearance": {
        "press_fit":      0.0,   # mm — interference
        "slip_fit":        0.1,  # mm — slides by hand
        "loose_fit":       0.3,  # mm — easily removable
    },
    "thread": {
        "M3":  {"pitch": 0.5, "tap_drill": 2.5},
        "M4":  {"pitch": 0.7, "tap_drill": 3.3},
        "M5":  {"pitch": 0.8, "tap_drill": 4.2},
        "M6":  {"pitch": 1.0, "tap_drill": 5.0},
        "M8":  {"pitch": 1.25, "tap_drill": 6.8},
        "M10": {"pitch": 1.5, "tap_drill": 8.5},
        "#4":  {"pitch": 0.7, "tap_drill": 2.7},   # 40-TPI approx
        "#6":  {"pitch": 0.8, "tap_drill": 3.4},
        "#8":  {"pitch": 0.9, "tap_drill": 4.1},
        "#10": {"pitch": 1.0, "tap_drill": 4.8},
    },
    "standard_fillets": {
        "3d_print": 1.0,   # mm — print-friendly
        "cnc":      0.5,   # mm — typical CNC
        "casting":  2.0,   # mm — draft + fillet
    },
}


# ---- Materials (density in g/cm³) ----------------------------------------

MATERIALS: dict[str, dict] = {
    "pla":            {"density": 1.25, "use": "3D print, prototyping"},
    "abs":            {"density": 1.05, "use": "3D print, functional"},
    "petg":           {"density": 1.27, "use": "3D print, durable"},
    "aluminum_6061":  {"density": 2.70, "use": "CNC, structural"},
    "aluminum_7075":  {"density": 2.81, "use": "CNC, high-stress"},
    "steel_1018":     {"density": 7.87, "use": "CNC, general"},
    "stainless_304":  {"density": 8.00, "use": "CNC, corrosion"},
    "brass":          {"density": 8.50, "use": "CNC, decorative"},
    "copper":         {"density": 8.96, "use": "CNC, electrical"},
    "delrin":         {"density": 1.41, "use": "CNC, low-friction"},
    "acrylic":        {"density": 1.18, "use": "Laser cut"},
    "birch_ply":      {"density": 0.68, "use": "Laser cut, structural"},
}


# ---- Export --------------------------------------------------------------

def export(result,
           name: str,
           formats: Iterable[str] = ("step", "stl"),
           out_dir: str = "/home/z/my-project/download/cad") -> dict[str, Path]:
    """Export a CadQuery result to multiple formats.

    Returns {format_name: path} for each successful export.
    Skips formats that fail (e.g., SVG for a 2D-only model).
    """
    import cadquery as cq
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    out: dict[str, Path] = {}
    for fmt in formats:
        if fmt not in EXPORTERS:
            print(f"WARNING: unknown format {fmt!r}, skipping")
            continue
        ext = EXPORTERS[fmt]["ext"]
        target = out_path / f"{name}.{ext}"
        try:
            if fmt == "stl":
                cq.exporters.export(result, str(target),
                                     tolerance=0.1, angularTolerance=0.1)
            elif fmt == "svg":
                cq.exporters.export(result, str(target),
                                     opt={
                                         "projectionDir": (1, 1, 1),
                                         "width": 200,
                                         "height": 200,
                                         "showAxes": False,
                                         "strokeWidth": 0.5,
                                     })
            else:
                cq.exporters.export(result, str(target))
            out[fmt] = target
        except Exception as exc:
            print(f"WARNING: {fmt} export failed: {exc}")
    return out


# ---- Inspection ----------------------------------------------------------

def bbox_summary(result) -> str:
    """Return bounding box dimensions as a human-readable string."""
    bb = result.val().BoundingBox()
    return (f"{bb.xlen:.2f} × {bb.ylen:.2f} × {bb.zlen:.2f} mm  "
            f"(center {bb.center.x:.1f}, {bb.center.y:.1f}, {bb.center.z:.1f})")


def mass_estimate(result, material: str = "pla") -> dict:
    """Estimate mass from volume × material density.

    Returns {volume_mm3, density_g_per_cm3, mass_g, material}.
    """
    if material not in MATERIALS:
        raise ValueError(f"Unknown material {material!r}; pick from {list(MATERIALS)}")
    vol = result.val().Volume()  # mm³
    density = MATERIALS[material]["density"]  # g/cm³
    mass_g = vol / 1000.0 * density  # mm³ → cm³ → g
    return {
        "volume_mm3": round(vol, 2),
        "density_g_per_cm3": density,
        "mass_g": round(mass_g, 2),
        "material": material,
    }


# ---- Script persistence --------------------------------------------------

def save_script(script_text: str, name: str,
                out_dir: str = "/home/z/my-project/scripts") -> Path:
    """Persist a parametric CAD script for re-runs."""
    p = Path(out_dir) / f"cad_{name}.py"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(script_text, encoding="utf-8")
    return p


# ---- Plate layout (for arranging multiple parts) -------------------------

def build_plate(parts: list, spacing_mm: float = 5.0) -> "cq.Workplane":
    """Arrange multiple parts side-by-side on a virtual cutting plate.

    parts: list of cq.Workplane objects.
    spacing_mm: gap between parts.
    Returns a single Workplane containing all parts translated.
    """
    import cadquery as cq
    if not parts:
        raise ValueError("parts list is empty")
    plate = cq.Workplane("XY")
    cursor_x = 0.0
    for p in parts:
        bb = p.val().BoundingBox()
        # Translate part so its min X is at cursor_x + spacing
        offset_x = cursor_x + spacing_mm - bb.xmin
        plate = plate.union(p.translate((offset_x, 0, 0)))
        cursor_x = bb.xlen + spacing_mm * 2
    return plate


# ---- Self-test ------------------------------------------------------------

# A parametric L-bracket demonstrating the helpers.
_DEMO_SCRIPT = '''\
"""Parametric L-bracket — generated by cad_helpers.py self-test."""
import cadquery as cq
import sys; sys.path.insert(0, "skill/cad/scripts")
from cad_helpers import export, bbox_summary, mass_estimate, PARAMS

# Parameters
L = 40          # arm length (mm)
W = 30          # width (mm)
T = 5           # thickness (mm)
HOLE_DIA = 5    # M5 clearance hole
FILLET = 1.0    # print-friendly fillet

# Build
bracket = (
    cq.Workplane("XY")
    .box(L, W, T)
    .faces(">Z").workplane()
    .moveTo(L/2 - 8, 0).hole(HOLE_DIA)
    # Bend up the second arm
    .faces(">X").workplane()
    .moveTo(0, -W/2).lineTo(0, W/2).lineTo(0, W/2 + T).close()
    .extrude(L)
    # Fillet all edges
    .edges().fillet(FILLET)
)

if __name__ == "__main__":
    print("Bounding box:", bbox_summary(bracket))
    print("Mass estimate:", mass_estimate(bracket, "pla"))
    paths = export(bracket, "l_bracket", ["step", "stl", "svg"])
    for fmt, p in paths.items():
        print(f"  {fmt}: {p}")
'''


if __name__ == "__main__":
    import cadquery as cq

    # Build a simpler bracket inline to verify the helpers work.
    L, W, T, HOLE_DIA = 40, 30, 5, 5
    bracket = (
        cq.Workplane("XY")
        .box(L, W, T)
        .faces(">Z").workplane()
        .moveTo(L/2 - 8, 0).hole(HOLE_DIA)
        .edges("|Z").fillet(1.0)
    )

    print("=== L-Bracket Demo ===")
    print("Bounding box:", bbox_summary(bracket))
    mass = mass_estimate(bracket, "pla")
    print(f"Volume: {mass['volume_mm3']} mm³, "
          f"Mass: {mass['mass_g']} g ({mass['material']})")

    paths = export(bracket, "l_bracket", ["step", "stl", "svg"])
    print("\nExported files:")
    for fmt, p in paths.items():
        size_kb = p.stat().st_size / 1024
        print(f"  {fmt}: {p}  ({size_kb:.1f} KB)")

    # Save the parametric script.
    script_path = save_script(_DEMO_SCRIPT, "l_bracket")
    print(f"\nParametric script: {script_path}")

    # Show available materials & threads.
    print(f"\nMaterials available: {len(MATERIALS)}")
    for name, info in list(MATERIALS.items())[:5]:
        print(f"  {name:<18} ρ={info['density']:.2f} g/cm³  ({info['use']})")
    print(f"  ... and {len(MATERIALS) - 5} more")

    print(f"\nThread specs available: {list(PARAMS['thread'].keys())}")
