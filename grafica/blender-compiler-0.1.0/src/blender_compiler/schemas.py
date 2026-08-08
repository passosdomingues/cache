"""Contratos de dados (Pydantic) trocados entre as camadas do pipeline.

Nenhuma camada deve importar tipos internos de outra camada: toda
comunicação passa por estes modelos, o que mantém baixo acoplamento
entre Pre Processing -> Vision -> Semantic -> Scene Graph -> Geometry -> Blender.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ViewAngle(str, Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"
    FORTY_FIVE_LEFT = "45_left"
    FORTY_FIVE_RIGHT = "45_right"
    TOP = "top"
    BOTTOM = "bottom"
    UNKNOWN = "unknown"


class PrimitiveType(str, Enum):
    CUBE = "cube"
    SPHERE = "sphere"
    CAPSULE = "capsule"
    CYLINDER = "cylinder"
    CONE = "cone"
    TORUS = "torus"
    PLANE = "plane"
    BEZIER = "bezier"
    CURVE = "curve"
    EXTRUDED_SILHOUETTE = "extruded_silhouette"



# ---------------------------------------------------------------------------
# Etapa 2: Pre Processing
# ---------------------------------------------------------------------------
class PreprocessedView(BaseModel):
    """Resultado do pré-processamento de UMA imagem/ângulo."""

    view_angle: ViewAngle
    source_path: str
    normalized_path: str
    mask_path: str
    silhouette_path: str
    edges_path: str
    depth_hint_path: str | None = None
    width: int
    height: int
    bbox: tuple[int, int, int, int] = Field(description="x, y, w, h da silhueta")
    fill_ratio: float = Field(description="área da máscara / área total da imagem")


class PreprocessingResult(BaseModel):
    object_name: str
    views: list[PreprocessedView]


# ---------------------------------------------------------------------------
# Etapa 3: Vision
# ---------------------------------------------------------------------------
class DetectedRegion(BaseModel):
    label: str
    bbox: tuple[float, float, float, float] = Field(description="x, y, w, h normalizado 0-1")
    confidence: float = 0.5
    dominant_color_rgb: tuple[int, int, int] | None = None
    notes: str = ""


class VisionViewAnalysis(BaseModel):
    view_angle: ViewAngle
    regions: list[DetectedRegion] = Field(default_factory=list)
    is_symmetrical_guess: bool = True
    raw_backend_output: dict = Field(default_factory=dict)


class VisionAnalysisResult(BaseModel):
    object_name: str
    backend_name: str
    views: list[VisionViewAnalysis]


# ---------------------------------------------------------------------------
# Etapa 4: Reconstrução Semântica
# ---------------------------------------------------------------------------
class PartMaterial(BaseModel):
    color_rgb: tuple[int, int, int] = (200, 200, 200)
    roughness: float = 0.6
    metallic: float = 0.0
    name: str | None = None


class Vec3(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


class SemanticPart(BaseModel):
    """Uma parte semântica do objeto/personagem (sem geometria ainda)."""

    id: str
    label: str
    parent_id: str | None = None
    relative_position: Vec3 = Field(
        default_factory=Vec3, description="posição relativa ao pai, unidades normalizadas"
    )
    relative_size: Vec3 = Field(default_factory=lambda: Vec3(x=1, y=1, z=1))
    symmetry_group: str | None = Field(default=None, description="ex: 'arm' liga left_arm/right_arm")
    material: PartMaterial = Field(default_factory=PartMaterial)
    suggested_primitive: PrimitiveType = PrimitiveType.CUBE
    tags: list[str] = Field(default_factory=list)


class SemanticModel(BaseModel):
    object_name: str
    object_class: str = Field(default="generic", description="ex: 'humanoid', 'prop', 'creature'")
    is_character: bool = False
    overall_dimensions: Vec3 = Field(default_factory=lambda: Vec3(x=1, y=1, z=2))
    parts: list[SemanticPart]

    def part_by_id(self, part_id: str) -> SemanticPart | None:
        return next((p for p in self.parts if p.id == part_id), None)


# ---------------------------------------------------------------------------
# Etapa 5: Scene Graph (serialização; o grafo em memória é networkx.DiGraph)
# ---------------------------------------------------------------------------
class SceneGraphNode(BaseModel):
    id: str
    label: str
    primitive: PrimitiveType
    position: Vec3
    size: Vec3
    material: PartMaterial
    symmetry_group: str | None = None


class SceneGraphEdge(BaseModel):
    source: str
    target: str
    relation: str = "parent_of"


class SceneGraphModel(BaseModel):
    object_name: str
    nodes: list[SceneGraphNode]
    edges: list[SceneGraphEdge]


# ---------------------------------------------------------------------------
# Etapa 6: Geometry Generator
# ---------------------------------------------------------------------------
class MeshData(BaseModel):
    node_id: str
    primitive: PrimitiveType
    vertices: list[tuple[float, float, float]]
    faces: list[tuple[int, ...]]
    position: Vec3
    rotation_euler: Vec3 = Field(default_factory=Vec3)
    scale: Vec3 = Field(default_factory=lambda: Vec3(x=1, y=1, z=1))
    material: PartMaterial
    parent_id: str | None = None


class GeometryModel(BaseModel):
    object_name: str
    meshes: list[MeshData]
    is_character: bool = False
    armature_bones: list[SceneGraphEdge] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Etapa 7/8: Export
# ---------------------------------------------------------------------------
class ExportResult(BaseModel):
    object_name: str
    blend_path: str | None = None
    gltf_path: str | None = None
    fbx_path: str | None = None
    obj_path: str | None = None
    used_blender: bool = False
    rigged: bool = False
    warnings: list[str] = Field(default_factory=list)
