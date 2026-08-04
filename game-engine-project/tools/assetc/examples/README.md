# Exemplo de uso do assetc

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
