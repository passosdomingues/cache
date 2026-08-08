"""Etapa 4 — Reconstrução Semântica.

Funde as análises de todas as views (Etapa 3) em um único `SemanticModel`:
partes, hierarquia, proporções, simetrias, materiais/cores e dimensões
relativas. Esta camada NUNCA gera vértices — apenas descreve "o que existe"
e "como se relaciona", deixando "como desenhar" para a Etapa 6.
"""

from __future__ import annotations

import logging

from blender_compiler.config import SemanticConfig
from blender_compiler.schemas import (
    PartMaterial,
    PrimitiveType,
    SemanticModel,
    SemanticPart,
    Vec3,
    ViewAngle,
    VisionAnalysisResult,
)

logger = logging.getLogger("blender_compiler.semantic")

# Hierarquia canônica para personagens humanoides. Usada quando os labels
# detectados batem com partes conhecidas; caso contrário cada região vira
# uma parte "solta" filha da raiz (objeto genérico).
_HUMANOID_HIERARCHY: dict[str, str | None] = {
    "torso": None,
    "head": "torso",
    "left_arm": "torso",
    "right_arm": "torso",
    "left_leg": "torso",
    "right_leg": "torso",
}

_SYMMETRY_GROUPS: dict[str, str] = {
    "left_arm": "arm",
    "right_arm": "arm",
    "left_leg": "leg",
    "right_leg": "leg",
}

_DEFAULT_PRIMITIVES: dict[str, PrimitiveType] = {
    "head": PrimitiveType.SPHERE,
    "torso": PrimitiveType.CUBE,
    "left_arm": PrimitiveType.CAPSULE,
    "right_arm": PrimitiveType.CAPSULE,
    "left_leg": PrimitiveType.CAPSULE,
    "right_leg": PrimitiveType.CAPSULE,
    "body": PrimitiveType.CUBE,
    "wheel": PrimitiveType.CYLINDER,
    "base": PrimitiveType.CUBE,
}


def _best_view_for_label(vision: VisionAnalysisResult, label: str):
    """Prioriza a view frontal para estimar posição/tamanho; cai para
    qualquer view que contenha o label."""
    priority = [ViewAngle.FRONT, ViewAngle.FORTY_FIVE_LEFT, ViewAngle.FORTY_FIVE_RIGHT]
    views_with_label = [(v, r) for v in vision.views for r in v.regions if r.label == label]
    if not views_with_label:
        return None, None
    for angle in priority:
        for v, r in views_with_label:
            if v.view_angle == angle:
                return v, r
    return views_with_label[0]


def reconstruct_semantics(
    vision: VisionAnalysisResult, cfg: SemanticConfig, object_name: str | None = None
) -> SemanticModel:
    all_labels: set[str] = {
        r.label for v in vision.views for r in v.regions if r.confidence >= cfg.min_part_confidence
    }
    if not all_labels:
        raise ValueError("Nenhuma região detectada pela camada Vision com confiança suficiente.")

    is_character = bool(all_labels & set(_HUMANOID_HIERARCHY))
    object_class = cfg.default_object_class if is_character else "generic"

    # Passo 1: calcula a posição/tamanho de cada parte no espaço da imagem
    # (coordenadas "mundiais" absolutas, derivadas do bbox 2D da view frontal).
    raw_positions: dict[str, Vec3] = {}
    raw_sizes: dict[str, Vec3] = {}
    parents: dict[str, str | None] = {}
    materials: dict[str, PartMaterial] = {}
    primitives: dict[str, PrimitiveType] = {}
    symmetry_groups: dict[str, str | None] = {}

    for label in sorted(all_labels):
        view, region = _best_view_for_label(vision, label)
        if region is None:
            continue

        x, y, w, h = region.bbox
        # eixo Y da imagem (baixo=+) é convertido para Z do mundo 3D (cima=+): inverte o sinal.
        raw_positions[label] = Vec3(x=(x + w / 2 - 0.5) * 2.0, y=0.0, z=(0.5 - (y + h / 2)) * 2.0)
        raw_sizes[label] = Vec3(x=w * 2.0, y=min(w, h) * 2.0, z=h * 2.0)
        parents[label] = _HUMANOID_HIERARCHY.get(label) if is_character else None
        symmetry_groups[label] = _SYMMETRY_GROUPS.get(label) if cfg.enforce_symmetry else None
        primitives[label] = _DEFAULT_PRIMITIVES.get(label, PrimitiveType.CUBE)
        color = region.dominant_color_rgb or (190, 190, 190)
        materials[label] = PartMaterial(color_rgb=color, name=f"mat_{label}")

    # Passo 2: converte posições absolutas em offsets RELATIVOS AO PAI —
    # é este offset que a Etapa 5 (Scene Graph) soma à posição absoluta do
    # pai para reconstruir a posição final. Sem este passo, partes filhas
    # ficariam deslocadas em dobro (posição absoluta + posição do pai).
    parts: list[SemanticPart] = []
    for label, raw_pos in raw_positions.items():
        parent_id = parents[label]
        if parent_id and parent_id in raw_positions:
            parent_pos = raw_positions[parent_id]
            rel_pos = Vec3(x=raw_pos.x - parent_pos.x, y=raw_pos.y - parent_pos.y, z=raw_pos.z - parent_pos.z)
        else:
            rel_pos = raw_pos

        parts.append(
            SemanticPart(
                id=label,
                label=label,
                parent_id=parent_id,
                relative_position=rel_pos,
                relative_size=raw_sizes[label],
                symmetry_group=symmetry_groups[label],
                material=materials[label],
                suggested_primitive=primitives[label],
                tags=[vision.backend_name],
            )
        )

    if cfg.enforce_symmetry:
        _mirror_missing_symmetric_parts(parts)

    return SemanticModel(
        object_name=object_name or vision.object_name,
        object_class=object_class,
        is_character=is_character,
        overall_dimensions=Vec3(x=1.0, y=1.0, z=2.0 if is_character else 1.0),
        parts=parts,
    )


def _mirror_missing_symmetric_parts(parts: list[SemanticPart]) -> None:
    """Se só um lado de um par simétrico foi detectado (ex: só left_arm
    apareceu em nenhuma view utilizável), espelha o lado existente em X."""
    by_id = {p.id: p for p in parts}
    pairs = [("left_arm", "right_arm"), ("left_leg", "right_leg")]
    for left_id, right_id in pairs:
        left, right = by_id.get(left_id), by_id.get(right_id)
        if left and not right:
            parts.append(_mirror_part(left, right_id))
        elif right and not left:
            parts.append(_mirror_part(right, left_id))


def _mirror_part(source: SemanticPart, new_id: str) -> SemanticPart:
    mirrored_pos = Vec3(
        x=-source.relative_position.x, y=source.relative_position.y, z=source.relative_position.z
    )
    return SemanticPart(
        id=new_id,
        label=new_id,
        parent_id=source.parent_id,
        relative_position=mirrored_pos,
        relative_size=source.relative_size.model_copy(),
        symmetry_group=source.symmetry_group,
        material=source.material.model_copy(),
        suggested_primitive=source.suggested_primitive,
        tags=source.tags + ["mirrored"],
    )
