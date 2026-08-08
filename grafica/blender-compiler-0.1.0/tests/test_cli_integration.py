from pathlib import Path

from cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_cli_compile_end_to_end(synthetic_humanoid_images: Path, tmp_path: Path):
    output_dir = tmp_path / "output"
    result = runner.invoke(
        app,
        ["compile", str(synthetic_humanoid_images), "--output", str(output_dir), "--name", "ci_test"],
    )

    assert result.exit_code == 0, result.output
    assert (output_dir / "01_preprocessing").exists()
    assert (output_dir / "02_vision" / "analysis.json").exists()
    assert (output_dir / "02b_semantic" / "semantic_model.json").exists()
    assert (output_dir / "03_scenegraph" / "scene_graph.json").exists()
    assert (output_dir / "03_geometry" / "ci_test.scene.json").exists()
    assert (output_dir / "export_result.json").exists()
    # Ao menos o OBJ (fallback ou real) deve sempre existir
    export_dir = output_dir / "04_export"
    assert any(export_dir.glob("*.obj"))


def test_cli_preprocess_then_reconstruct(synthetic_humanoid_images: Path, tmp_path: Path):
    output_dir = tmp_path / "output"

    pre_result = runner.invoke(
        app, ["preprocess", str(synthetic_humanoid_images), "--output", str(output_dir), "--name", "ci_test2"]
    )
    assert pre_result.exit_code == 0, pre_result.output

    rec_result = runner.invoke(app, ["reconstruct", str(output_dir), "--name", "ci_test2"])
    assert rec_result.exit_code == 0, rec_result.output
    assert (output_dir / "03_geometry" / "ci_test2.scene.json").exists()
