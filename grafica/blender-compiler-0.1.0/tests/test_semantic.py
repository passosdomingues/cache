from blender_compiler.config import SemanticConfig
from blender_compiler.schemas import DetectedRegion, ViewAngle, VisionAnalysisResult, VisionViewAnalysis
from blender_compiler.semantic.pipeline import reconstruct_semantics


def _fake_vision_result(labels: list[str]) -> VisionAnalysisResult:
    regions = [
        DetectedRegion(label=label, bbox=(0.1 * i, 0.1, 0.2, 0.2), confidence=0.9)
        for i, label in enumerate(labels)
    ]
    return VisionAnalysisResult(
        object_name="test",
        backend_name="mock",
        views=[VisionViewAnalysis(view_angle=ViewAngle.FRONT, regions=regions)],
    )


def test_reconstruct_semantics_builds_hierarchy():
    vision = _fake_vision_result(["head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"])
    model = reconstruct_semantics(vision, SemanticConfig())

    assert model.is_character is True
    assert model.object_class == "humanoid"
    part_ids = {p.id for p in model.parts}
    assert "torso" in part_ids
    torso = model.part_by_id("torso")
    head = model.part_by_id("head")
    assert torso.parent_id is None
    assert head.parent_id == "torso"


def test_reconstruct_semantics_mirrors_missing_limb():
    vision = _fake_vision_result(["torso", "left_arm"])  # falta right_arm
    model = reconstruct_semantics(vision, SemanticConfig(enforce_symmetry=True))

    right_arm = model.part_by_id("right_arm")
    assert right_arm is not None
    assert "mirrored" in right_arm.tags


def test_reconstruct_semantics_generic_object():
    vision = _fake_vision_result(["body"])
    model = reconstruct_semantics(vision, SemanticConfig())
    assert model.is_character is False
    assert model.object_class == "generic"


def test_reconstruct_semantics_raises_without_regions():
    vision = VisionAnalysisResult(
        object_name="empty",
        backend_name="mock",
        views=[VisionViewAnalysis(view_angle=ViewAngle.FRONT, regions=[])],
    )
    try:
        reconstruct_semantics(vision, SemanticConfig())
        assert False
    except ValueError:
        pass
