from pathlib import Path

from blender_compiler.config import PreprocessingConfig
from blender_compiler.preprocessing.pipeline import infer_view_angle, run_preprocessing
from blender_compiler.schemas import ViewAngle


def test_infer_view_angle():
    assert infer_view_angle("front.png") == ViewAngle.FRONT
    assert infer_view_angle("45_left.png") == ViewAngle.FORTY_FIVE_LEFT
    assert infer_view_angle("45_right.jpg") == ViewAngle.FORTY_FIVE_RIGHT
    assert infer_view_angle("character_back_view.png") == ViewAngle.BACK
    assert infer_view_angle("mystery.png") == ViewAngle.UNKNOWN


def test_run_preprocessing_generates_all_artifacts(synthetic_humanoid_images: Path, tmp_path: Path):
    output_dir = tmp_path / "output"
    cfg = PreprocessingConfig(background_removal_method="threshold")

    result = run_preprocessing(synthetic_humanoid_images, output_dir, cfg, object_name="test_obj")

    assert len(result.views) == 6
    for view in result.views:
        assert Path(view.normalized_path).exists()
        assert Path(view.mask_path).exists()
        assert Path(view.silhouette_path).exists()
        assert Path(view.edges_path).exists()
        assert 0.0 < view.fill_ratio < 1.0
        assert view.width > 0 and view.height > 0


def test_run_preprocessing_raises_on_empty_dir(tmp_path: Path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    cfg = PreprocessingConfig()
    try:
        run_preprocessing(empty_dir, tmp_path / "out", cfg)
        assert False, "deveria ter levantado FileNotFoundError"
    except FileNotFoundError:
        pass
