from pathlib import Path

from blender_compiler.config import PreprocessingConfig, VisionConfig
from blender_compiler.preprocessing.pipeline import run_preprocessing
from blender_compiler.vision.mock_backend import MockVisionBackend
from blender_compiler.vision.pipeline import build_backend, run_vision


def test_build_backend_mock():
    backend = build_backend(VisionConfig(backend="mock"))
    assert isinstance(backend, MockVisionBackend)


def test_build_backend_unknown_raises():
    try:
        build_backend(VisionConfig(backend="does_not_exist"))
        assert False
    except ValueError:
        pass


def test_mock_backend_detects_humanoid_regions(synthetic_humanoid_images: Path, tmp_path: Path):
    pre_cfg = PreprocessingConfig(background_removal_method="threshold")
    pre_result = run_preprocessing(synthetic_humanoid_images, tmp_path / "output", pre_cfg, "test_obj")

    vision_result = run_vision(pre_result, VisionConfig(backend="mock"), object_hint="humanoid")

    assert vision_result.backend_name == "mock"
    assert len(vision_result.views) == 6
    labels = {r.label for v in vision_result.views for r in v.regions}
    assert {"head", "torso", "left_arm", "right_arm", "left_leg", "right_leg"} <= labels
