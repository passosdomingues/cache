"""Etapa 5 — Scene Graph.

Converte o `SemanticModel` (Etapa 4) em um `networkx.DiGraph`, onde cada nó
é uma parte do objeto e cada aresta representa dependência espacial
(parent -> child). Esta camada resolve posições ABSOLUTAS a partir das
posições relativas herdadas na hierarquia.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import networkx as nx

from blender_compiler.schemas import (
    SceneGraphEdge,
    SceneGraphModel,
    SceneGraphNode,
    SemanticModel,
    Vec3,
)

logger = logging.getLogger("blender_compiler.scenegraph")


def build_scene_graph(model: SemanticModel) -> nx.DiGraph:
    graph = nx.DiGraph(object_name=model.object_name, is_character=model.is_character)

    for part in model.parts:
        graph.add_node(
            part.id,
            label=part.label,
            primitive=part.suggested_primitive,
            relative_position=part.relative_position,
            size=part.relative_size,
            material=part.material,
            symmetry_group=part.symmetry_group,
        )

    for part in model.parts:
        if part.parent_id and part.parent_id in graph.nodes:
            graph.add_edge(part.parent_id, part.id, relation="parent_of")

    # garante DAG (sem ciclos) — requisito para resolver posições absolutas
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Scene graph contém ciclo — hierarquia de partes inválida.")

    _resolve_absolute_positions(graph)
    return graph


def _resolve_absolute_positions(graph: nx.DiGraph) -> None:
    """Soma recursivamente a posição relativa de cada nó à posição absoluta
    do seu pai (BFS a partir das raízes), armazenando em `absolute_position`."""
    roots = [n for n, d in graph.in_degree() if d == 0]
    for root in roots:
        graph.nodes[root]["absolute_position"] = graph.nodes[root]["relative_position"]
        for parent, child in nx.bfs_edges(graph, root):
            p_pos: Vec3 = graph.nodes[parent]["absolute_position"]
            rel: Vec3 = graph.nodes[child]["relative_position"]
            graph.nodes[child]["absolute_position"] = Vec3(
                x=p_pos.x + rel.x, y=p_pos.y + rel.y, z=p_pos.z + rel.z
            )


def to_scene_graph_model(graph: nx.DiGraph) -> SceneGraphModel:
    nodes = [
        SceneGraphNode(
            id=n,
            label=d["label"],
            primitive=d["primitive"],
            position=d.get("absolute_position", d["relative_position"]),
            size=d["size"],
            material=d["material"],
            symmetry_group=d.get("symmetry_group"),
        )
        for n, d in graph.nodes(data=True)
    ]
    edges = [
        SceneGraphEdge(source=u, target=v, relation=d.get("relation", "parent_of"))
        for u, v, d in graph.edges(data=True)
    ]
    return SceneGraphModel(object_name=graph.graph["object_name"], nodes=nodes, edges=edges)


def save_scene_graph(graph: nx.DiGraph, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    model = to_scene_graph_model(graph)

    json_path = out_dir / "scene_graph.json"
    json_path.write_text(model.model_dump_json(indent=2), encoding="utf-8")

    graphml_path = out_dir / "scene_graph.graphml"
    export_graph = graph.copy()
    for _, data in export_graph.nodes(data=True):
        for key in (
            "relative_position",
            "absolute_position",
            "size",
            "material",
            "primitive",
            "symmetry_group",
        ):
            if key in data:
                data[key] = json.dumps(
                    data[key].model_dump() if hasattr(data[key], "model_dump") else data[key],
                    default=str,
                )
    nx.write_graphml(export_graph, graphml_path)

    mermaid_path = out_dir / "scene_graph.mmd"
    mermaid_path.write_text(_to_mermaid(model), encoding="utf-8")

    return {"json": json_path, "graphml": graphml_path, "mermaid": mermaid_path}


def _to_mermaid(model: SceneGraphModel) -> str:
    lines = ["graph TD"]
    for node in model.nodes:
        lines.append(f'    {node.id}["{node.label}<br/>{node.primitive.value}"]')
    for edge in model.edges:
        lines.append(f"    {edge.source} --> {edge.target}")
    return "\n".join(lines)
