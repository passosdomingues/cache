# Exemplo de uso do assetc

## Front-end "raw" (Sprint 3)

```bash
# a partir da raiz do projeto, depois de `make build`:
./build/tools/assetc/assetc build \
    --manifest=tools/assetc/examples/assets.manifest \
    --out=build/example.pkg

./build/tools/assetc/assetc inspect build/example.pkg

# rode de novo sem mudar nada: os dois assets devem vir do cache
./build/tools/assetc/assetc build \
    --manifest=tools/assetc/examples/assets.manifest \
    --out=build/example.pkg
```

## Front-ends "image" + "atlas" (Sprint 4)

Requer ImageMagick instalado (`sudo apt install imagemagick`).

```bash
./build/tools/assetc/assetc build \
    --manifest=tools/assetc/examples/atlas.manifest \
    --out=build/atlas-example.pkg

./build/tools/assetc/assetc inspect build/atlas-example.pkg
```

`hero_atlas` empacota `hero_body` e `hero_head` (ambos `type=image`) em um
único atlas, com mipmaps e payload comprimido (deflate/zlib). Mudar
apenas `hero_head.png` e rodar de novo mostra `hero_body` vindo do cache
e `hero_head`/`hero_atlas` recompilados — a invalidação se propaga pelo
grafo de dependências.
