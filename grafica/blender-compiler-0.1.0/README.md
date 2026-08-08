# Blender Compiler

**Compilador de geometria procedural**: converte múltiplas imagens (front, back, left, right, 45°...)
de um objeto ou personagem em um arquivo `.blend` **low poly**, usando apenas
ferramentas open source, 100% via linha de comando.

> Este projeto **não** tenta reproduzir modelos de reconstrução 3D fotorrealista
> (tipo Hunyuan3D). O objetivo é um pipeline determinístico e modular que
> interpreta a silhueta/estrutura do objeto e monta a cena com **primitivas
> geométricas** (cubos, esferas, cápsulas, cilindros...), no espírito de um
> "compilador": entrada estruturada → representação intermediária → saída.

## Arquitetura

```
images/
    ↓
Pre Processing      (OpenCV: bg removal, silhueta, bordas, profundidade aprox.)
    ↓
Vision Pipeline     (interface plugável p/ Vision LLM: Qwen-VL, LLaMA-Vision, MiniCPM, Moondream, ou heurística offline)
    ↓
Semantic Reconstruction  (JSON: partes, hierarquia, proporções, simetrias, materiais)
    ↓
Scene Graph         (NetworkX DiGraph: nós = partes, arestas = dependência espacial)
    ↓
Geometry Generator  (primitivas: cube, sphere, capsule, cylinder, cone, torus, plane, bezier/curve)
    ↓
Blender (bpy via CLI headless)  (objetos, coleções, materiais, UV, armature/rig)
    ↓
.blend  (+ glTF, OBJ, FBX opcional)
```

Cada camada é um módulo Python independente em `src/blender_compiler/`,
comunicando-se apenas por meio dos contratos Pydantic definidos em
`src/blender_compiler/schemas.py`. Veja [`docs/architecture.md`](docs/architecture.md)
para diagramas Mermaid detalhados de cada etapa.

## Instalação rápida (Linux Mint / Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y blender python3 python3-pip
git clone <este-repositorio> blender-compiler
cd blender-compiler
make build     # instala dependências Python (requirements-dev.txt)
```

## Uso

```bash
# Pipeline completo: images/ -> .blend
python3 cli.py compile input/ --output output/ --name meu_personagem

# Etapas isoladas
python3 cli.py preprocess input/ --output output/ --name meu_personagem
python3 cli.py reconstruct output/ --name meu_personagem   # Vision + Semantic + Scene Graph + Geometry
python3 cli.py export output/ --name meu_personagem        # apenas Etapa 7/8 (Blender)
```

Ou via `make`:

```bash
make run OBJECT_NAME=meu_personagem INPUT_DIR=input OUTPUT_DIR=output
make demo     # gera imagens sintéticas de exemplo e roda o pipeline completo
make test     # roda a suíte de testes (pytest)
make lint     # ruff + black --check + mypy
make release  # empacota tudo em dist/blender-compiler-<versão>.zip
```

### Formato de entrada esperado

```
input/
  front.png
  back.png
  left.png
  right.png
  45_left.png
  45_right.png
```

A quantidade de imagens é livre — o sistema aceita de 1 a N vistas (mais
vistas = reconstrução mais precisa). O ângulo de cada imagem é inferido pelo
nome do arquivo (`front`, `back`, `left`, `right`, `45_left`, `45_right`,
`top`, `bottom`); se não reconhecido, é marcado como `unknown` e ainda assim
processado.

### Saída gerada

```
output/
  01_preprocessing/<view>/{normalized,mask,silhouette,edges,depth_hint}.png
  02_vision/analysis.json
  02b_semantic/semantic_model.json
  03_scenegraph/{scene_graph.json,scene_graph.graphml,scene_graph.mmd}
  03_geometry/<nome>.scene.json
  04_export/<nome>.{blend,glb,obj,fbx,mtl}
  export_result.json
```

## Docker

```bash
make docker-build
make docker-run OBJECT_NAME=meu_personagem   # usa ./input e ./output do host
make shell                                    # shell interativo dentro do container
```

A imagem Docker instala o **Blender real** via `apt` (não o pacote pip `bpy`,
que é não-oficial), garantindo um build reproduzível e completo — veja
[`Dockerfile`](Dockerfile).

## Trocando o backend de Vision LLM

Em `config/default.yaml`:

```yaml
vision:
  backend: qwen_vl        # mock | qwen_vl | llama_vision | minicpm | moondream | http_generic
  endpoint: "http://localhost:11434"   # servidor compatível com Ollama
  model_name: "qwen2.5-vl"
```

O backend `mock` (padrão) usa heurísticas de visão computacional clássica
(sem nenhum modelo de IA) — ideal para desenvolvimento offline e testes
determinísticos. Qualquer servidor de inferência multimodal compatível com a
API `/api/generate` do Ollama funciona plugando `endpoint` + `model_name`.
Veja [`docs/api.md`](docs/api.md) para o contrato completo de `VisionBackend`.

## Extensibilidade

| Quero adicionar...              | Onde mexer                                                        |
|----------------------------------|---------------------------------------------------------------------|
| Uma nova primitiva geométrica    | `src/blender_compiler/geometry/primitives.py` (registrar em `PRIMITIVE_BUILDERS`) |
| Um novo backend de Vision LLM    | `src/blender_compiler/vision/` (implementar `VisionBackend`)       |
| Uma nova regra de hierarquia semântica (ex: quadrúpede) | `src/blender_compiler/semantic/pipeline.py` |
| Um novo formato de exportação    | `src/blender_compiler/blender_export/blender_build_script.py`      |
| Fotogrametria / NeRF / Gaussian Splatting / text-to-3D | novo módulo implementando a mesma interface de `PreprocessingResult` → substitui a Etapa 2/3 |

## Testes

```bash
make test
```

27 testes cobrindo: pré-processamento (OpenCV), backend de visão mock,
reconstrução semântica (hierarquia, simetria, espelhamento de membros
ausentes), scene graph (DAG, detecção de ciclo), todas as primitivas
geométricas, exportação (fallback OBJ e Blender real quando disponível), e
o pipeline completo via CLI.

## Status e limitações conhecidas

- O backend `mock` de Vision usa heurísticas geométricas simples (proporções
  de bounding box), não um modelo de IA real — é o ponto de partida
  determinístico; plugar um Vision LLM real via `http_generic` é a via
  para reconstrução mais fiel.
- A malha gerada é sempre low poly por primitivas — não há reconstrução de
  detalhes finos de superfície (isso é uma decisão de design, não uma limitação
  a corrigir).
- Suporte a curvas Bézier (`bezier`/`curve`) gera pontos de controle, mas a
  conversão para objeto `CURVE` do Blender e sua união com malhas ainda é
  uma extensão futura (ver `docs/architecture.md#roadmap`).

## Licença

MIT — veja [`LICENSE`](LICENSE).
