# Guia de Contribuição

Obrigado por considerar contribuir com o Blender Compiler! Este documento
descreve como propor mudanças mantendo a arquitetura em camadas íntegra.

## Princípios do projeto (leia antes de codar)

1. **Uma camada, uma responsabilidade.** Pre Processing nunca interpreta
   semântica. Semantic nunca gera vértices. Geometry nunca conhece Blender.
   Se sua mudança cruza essa fronteira, provavelmente pertence a outro
   módulo ou precisa de um novo contrato em `schemas.py`.
2. **Comunicação só via `schemas.py`.** Nenhum módulo importa tipos internos
   de outro — apenas os modelos Pydantic compartilhados.
3. **Nada hardcoded.** Todo parâmetro de comportamento vai em
   `config/default.yaml` / `PipelineConfig`.
4. **`bpy` só existe em um arquivo.** Todo o resto do pipeline deve
   continuar testável sem o Blender instalado
   (`blender_export/blender_build_script.py` é a única exceção).

## Configurando o ambiente de desenvolvimento

```bash
git clone <repo> && cd blender-compiler
python3 -m venv .venv && source .venv/bin/activate
make build            # instala requirements-dev.txt
sudo apt-get install -y blender   # opcional, mas recomendado p/ rodar Etapa 7 de verdade
```

## Fluxo de trabalho

```bash
make format   # ruff --fix + black
make lint     # ruff check + black --check + mypy
make test     # pytest -v --cov
```

Todo PR deve passar em `make lint` e `make test` antes de ser aberto.

## Adicionando funcionalidades comuns

### Nova primitiva geométrica
1. Escreva `build_<nome>(size, **kwargs) -> (vertices, faces)` em
   `src/blender_compiler/geometry/primitives.py`.
2. Registre em `PRIMITIVE_BUILDERS`.
3. Adicione ao `PrimitiveType` enum em `schemas.py`.
4. Teste em `tests/test_geometry.py` (siga o padrão parametrizado existente).

### Novo backend de Vision LLM
1. Se for um servidor HTTP compatível com Ollama, basta adicionar uma
   entrada em `KNOWN_MODEL_DEFAULTS` (`vision/http_backend.py`) — zero
   código novo.
2. Se precisar de um protocolo diferente, implemente `VisionBackend`
   (`vision/base.py`) em um novo arquivo e registre em
   `vision/pipeline.py::build_backend()`.
3. Teste com um mock de rede ou o backend `mock` como fallback determinístico.

### Nova regra de hierarquia semântica (ex: quadrúpede, veículo)
Edite `src/blender_compiler/semantic/pipeline.py`: adicione um novo
dicionário de hierarquia (como `_HUMANOID_HIERARCHY`) e a lógica de seleção
de qual hierarquia usar com base nos labels detectados.

### Novo formato de exportação
Adicione a chamada `bpy.ops.export_scene.*` correspondente em
`blender_build_script.py`, seguindo o padrão de `--gltf`/`--fbx`/`--obj`.

## Testes

- Testes unitários por camada em `tests/test_<camada>.py`.
- `tests/conftest.py` fornece a fixture `synthetic_humanoid_images`
  (gera imagens determinísticas via OpenCV, sem depender de arquivos externos).
- `tests/test_cli_integration.py` cobre o pipeline completo via `CliRunner`.
- Testes que dependem do Blender real usam
  `@pytest.mark.skipif(shutil.which("blender") is None, ...)` para não
  quebrar em ambientes sem Blender instalado.

## Estilo de código

- Python 3.12, tipado (type hints em toda função pública).
- `ruff` (import sorting, pyupgrade, bugbear) + `black` (line-length 110).
- Docstrings em português explicando a *responsabilidade* do módulo, não
  apenas "o que" o código faz.
- Commits pequenos e descritivos; um PR por funcionalidade.

## Reportando bugs

Abra uma issue com: comando exato executado, `config/default.yaml` usado,
saída de `logs/run_*.log`, e (se possível) as imagens de entrada ou uma
descrição de como reproduzir com `scripts/generate_example_images.py`.
