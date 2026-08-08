# docker/

O `Dockerfile` e o `docker-compose.yml` principais ficam na raiz do projeto
(convenção padrão para builds `docker build .` sem precisar de `-f`).

Esta pasta guarda material de apoio ao ambiente Docker:

- Notas de troubleshooting de build (pacotes `blender`/OpenCV via apt).
- Local reservado para Dockerfiles alternativos (ex: `Dockerfile.gpu` no futuro).

## Build reproduzível

```bash
make docker-build     # equivalente a: docker build -t blender-compiler:latest -f Dockerfile .
make docker-run OBJECT_NAME=meu_personagem
make shell             # abre um shell dentro do container para debug
```

A imagem instala o pacote `blender` via `apt` (repositório `universe` do
Ubuntu 24.04), garantindo um Blender real e completo (não o pacote `bpy`
via pip, que é não-oficial e pesado). O CLI do projeto invoca
`blender --background --python ...` internamente — veja
`src/blender_compiler/blender_export/pipeline.py`.
