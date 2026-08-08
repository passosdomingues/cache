# API / Contratos entre camadas

Todos os modelos abaixo estão definidos em `src/blender_compiler/schemas.py`
(Pydantic). Nenhuma camada deve depender de tipos internos de outra camada
— apenas destes contratos.

## CLI

```
python3 cli.py compile <input_dir> [--output DIR] [--name NOME] [--config YAML]
python3 cli.py preprocess <input_dir> [--output DIR] [--name NOME] [--config YAML]
python3 cli.py reconstruct <output_dir> [--name NOME] [--config YAML]
python3 cli.py export <output_dir> [--name NOME] [--config YAML]
```

| Comando       | Etapas executadas                                        | Pré-requisito                          |
|---------------|-----------------------------------------------------------|------------------------------------------|
| `compile`     | 1 a 8 (pipeline completo)                                  | diretório de imagens                     |
| `preprocess`  | 2 (Pre Processing)                                          | diretório de imagens                     |
| `reconstruct` | 3-6 (Vision, Semantic, Scene Graph, Geometry)              | `output/01_preprocessing/_result.json` (gerado por `preprocess`) |
| `export`      | 7-8 (Blender + Rig)                                        | `output/03_geometry/<nome>.scene.json` (gerado por `compile`/`reconstruct`) |

## Contratos principais

### `PreprocessedView` / `PreprocessingResult`
Saída da Etapa 2. Um `PreprocessedView` por imagem: caminhos para
normalizada/máscara/silhueta/bordas/depth-hint, bbox e `fill_ratio`.

### `VisionViewAnalysis` / `VisionAnalysisResult`
Saída da Etapa 3. Lista de `DetectedRegion` (label, bbox normalizado 0-1,
confiança, cor dominante) por view.

### `VisionBackend` (interface plugável)

```python
class VisionBackend(ABC):
    name: str
    @abstractmethod
    def analyze_view(self, view: PreprocessedView, object_hint: str = "") -> VisionViewAnalysis: ...
```

Implementações disponíveis: `MockVisionBackend` (heurística offline),
`HttpVisionBackend` (qualquer servidor `/api/generate` estilo Ollama —
usado por Qwen-VL, LLaMA-Vision, MiniCPM, Moondream via `model_name`).

Para adicionar um backend totalmente novo (ex: SDK proprietário), implemente
`VisionBackend` e registre em `vision/pipeline.py::build_backend()`.

### `SemanticModel` / `SemanticPart`
Saída da Etapa 4. `SemanticPart` tem `id`, `label`, `parent_id`,
`relative_position` (Vec3), `relative_size` (Vec3), `symmetry_group`,
`material` (`PartMaterial`), `suggested_primitive` (`PrimitiveType`).
**Nunca contém vértices.**

### `SceneGraphModel` / `SceneGraphNode` / `SceneGraphEdge`
Saída da Etapa 5 (serialização do `networkx.DiGraph`). Cada nó tem posição
**absoluta** já resolvida (soma das posições relativas ao longo da
hierarquia).

### `GeometryModel` / `MeshData`
Saída da Etapa 6. `MeshData` tem `vertices: list[tuple[float,float,float]]`,
`faces: list[tuple[int,...]]` (polígonos N-gonais, não necessariamente
triangulados), `position`, `material`, `parent_id`.

### `ExportResult`
Saída da Etapa 7/8: caminhos para `.blend`/`.glb`/`.obj`/`.fbx` gerados,
flags `used_blender` e `rigged`, e `warnings` (ex: quando o fallback OBJ foi
usado por falta do executável Blender).

## Primitivas geométricas (`geometry/primitives.py`)

```python
PRIMITIVE_BUILDERS: dict[str, Callable[..., tuple[list[Vertex], list[Face]]]] = {
    "cube": build_cube,
    "plane": build_plane,
    "sphere": build_uv_sphere,
    "cylinder": build_cylinder,
    "cone": build_cone,
    "capsule": build_capsule,
    "torus": build_torus,
    "bezier": build_bezier_curve_points,
    "curve": build_bezier_curve_points,
}
```

Toda função tem assinatura `(size: tuple[float,float,float], **kwargs) ->
(vertices, faces)`, com vértices centrados na origem. Para registrar uma
primitiva nova (ex: `pyramid`), basta escrever a função e adicionar a
entrada no dicionário — nenhuma outra camada precisa ser alterada.

## Configuração (`config/default.yaml`)

Ver `src/blender_compiler/config.py` para o schema Pydantic completo
(`PipelineConfig`). Todo parâmetro do pipeline é configurável por YAML —
nada é hardcoded no código das camadas.
