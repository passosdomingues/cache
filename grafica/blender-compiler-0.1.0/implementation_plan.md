# Implementation Plan - Faithful 3D Image-to-Primitive Reconstruction

Enhance the 3D model fidelity of `blender-compiler` to match the exact input image outline (e.g. `Apkallu.png` with wings, crown, accessories) rather than fallback humanoid box ratios.

## System & Hardware Context
- **CPU**: Intel i7-8565U (8 vCPUs @ 2.0GHz)
- **RAM**: 16 GB DDR4
- **Ollama**: Installed at `/usr/local/bin/ollama`

## Key Improvements

### 1. Contour-Based 3D Silhouette Extrusion & Visual Hull Generator
- **Problem**: Previously, `MockVisionBackend` applied a generic 6-box mannequin ratio regardless of the image silhouette, discarding wings, crowns, bird/fish features, or unique silhouettes.
- **Solution**:
  - Extract exact 2D contours from the preprocessed binary mask using OpenCV (`findContours` + `approxPolyDP` for controlled low-poly vertex count).
  - Create a new primitive type `EXTRUDED_SILHOUETTE` / `POLYGON_PRIMITIVE` that extrudes the true silhouette outline into 3D.
  - When multi-view images (front + side) are supplied, intersect their extruded silhouettes (Visual Hull CSG) to form a true 3D low-poly representation of the exact object shape.

### 2. Intelligent Contour Convexity & Blob Decomposition
- Analyze the 2D contour convexity defects and distance transform peaks to split complex shapes (e.g., wings, head, body, tail, held items) into true bounding primitive parts based on the image's actual geometry.

### 3. Ollama Vision LLM Integration Tailored for 16GB CPU Hardware
- Support lightweight, high-fidelity vision models on CPU:
  - `moondream` (~1.4B, ~800MB RAM, fast response on CPU).
  - `qwen2.5-vl:3b` (~3B, ~2.2GB RAM, highly accurate bounding box & part decomposition).
- Auto-start `ollama serve` service if not running.
- Prompt templates tuned to request normalized 3D bounding boxes `(x, y, z, dx, dy, dz)` and primitive suggestions (`extrusions`, `cubes`, `cylinders`, `cones`).

---

## Proposed Changes

### Vision & Computer Vision

#### [MODIFY] [src/blender_compiler/vision/mock_backend.py](file:///home/rafael/github/cache/grafica/blender-compiler-0.1.0/src/blender_compiler/vision/mock_backend.py)
- Replace static percentage humanoid layout with dynamic contour blob detection and distance transform peak splitting.

#### [MODIFY] [src/blender_compiler/vision/ollama.py](file:///home/rafael/github/cache/grafica/blender-compiler-0.1.0/src/blender_compiler/vision/ollama.py)
- Add Ollama server manager (auto-check/start daemon) and enhanced structured JSON prompt for Qwen2.5-VL / Moondream.

---

### Geometry & Primitives

#### [NEW] [src/blender_compiler/geometry/extrude.py](file:///home/rafael/github/cache/grafica/blender-compiler-0.1.0/src/blender_compiler/geometry/extrude.py)
- Implement low-poly 2D contour extrusion to 3D mesh (`MeshData` builder for polygonal silhouette primitives).

#### [MODIFY] [src/blender_compiler/geometry/primitives.py](file:///home/rafael/github/cache/grafica/blender-compiler-0.1.0/src/blender_compiler/geometry/primitives.py)
- Register `EXTRUDED_SILHOUETTE` primitive builder.

#### [MODIFY] [src/blender_compiler/blender_export/openscad.py](file:///home/rafael/github/cache/grafica/blender-compiler-0.1.0/src/blender_compiler/blender_export/openscad.py)
- Add OpenSCAD `linear_extrude` or 3D polygon mesh support for extruded silhouettes.

---

## Verification Plan

### Automated Tests
- Test contour polygon extraction & low-poly simplification in `test_preprocessing.py`.
- Test 3D extrusion mesh generation in `test_geometry.py`.
- Test OpenSCAD code generation for extruded silhouettes in `test_openscad.py`.

### Manual Verification
- Run `python cli.py compile input/ --name apkallu` on `Apkallu.png` and verify the resulting `.blend`, `.scad`, `.obj`, `.glb` match the winged Apkallu figure silhouette.
