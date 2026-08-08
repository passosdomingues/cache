import networkx as nx
import pytest

from blender_compiler.scenegraph.pipeline import build_scene_graph, save_scene_graph, to_scene_graph_model
from blender_compiler.schemas import SemanticModel, SemanticPart, Vec3


def _simple_model() -> SemanticModel:
    return SemanticModel(
        object_name="test",
        object_class="humanoid",
        is_character=True,
        parts=[
            SemanticPart(id="torso", label="torso", parent_id=None, relative_position=Vec3(x=0, y=0, z=0)),
            SemanticPart(id="head", label="head", parent_id="torso", relative_position=Vec3(x=0, y=0, z=0.5)),
        ],
    )


def test_build_scene_graph_is_dag_with_absolute_positions():
    graph = build_scene_graph(_simple_model())
    assert nx.is_directed_acyclic_graph(graph)
    assert graph.nodes["head"]["absolute_position"].z == pytest.approx(0.5)
    assert graph.nodes["torso"]["absolute_position"].z == pytest.approx(0.0)


def test_build_scene_graph_detects_cycle():
    model = _simple_model()
    model.parts[0].parent_id = "head"  # cria ciclo torso -> head -> torso
    with pytest.raises(ValueError):
        build_scene_graph(model)


def test_save_scene_graph_writes_artifacts(tmp_path):
    graph = build_scene_graph(_simple_model())
    paths = save_scene_graph(graph, tmp_path / "sg")
    assert paths["json"].exists()
    assert paths["graphml"].exists()
    assert paths["mermaid"].exists()
    assert "graph TD" in paths["mermaid"].read_text()


def test_to_scene_graph_model_roundtrip():
    graph = build_scene_graph(_simple_model())
    model = to_scene_graph_model(graph)
    assert len(model.nodes) == 2
    assert len(model.edges) == 1
    assert model.edges[0].source == "torso"
    assert model.edges[0].target == "head"
