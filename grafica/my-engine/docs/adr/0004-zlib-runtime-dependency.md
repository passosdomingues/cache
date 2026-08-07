# ADR 0004 — zlib como Dependência de Runtime

## Status
Aceito

## Contexto
O RFC 00 (Visão Arquitetural) restringe bibliotecas externas à Toolchain:
"Bibliotecas externas usadas apenas na Toolchain (ex: ImageMagick,
FFmpeg) para pipelines de assets, não no runtime." Essas ferramentas são
CLIs pesadas, chamadas via subprocesso, usadas apenas durante a
compilação de assets (`assetc`).

A partir do Sprint 6 (Resource Manager), o runtime passa a **consumir**
pacotes `game.pkg` — e os payloads de assets `image`/`atlas`/`audio` são
comprimidos com deflate (zlib) pelo asset compiler (Sprints 4-5). Sem
suporte a descompressão no runtime, esses assets não podem ser
carregados.

## Pergunta
zlib conta como a mesma categoria de dependência que ImageMagick/FFmpeg,
proibida no runtime pelo RFC 00?

## Decisão
**Não.** zlib é tratado como uma exceção explícita e é permitido no
runtime, distinto de ImageMagick/FFmpeg pelos seguintes critérios:

1. **Tamanho e natureza:** zlib é uma biblioteca C pequena, estável,
   embutível (linkagem estática/dinâmica direta) — não uma ferramenta de
   linha de comando pesada com dezenas de dependências de sistema
   (codecs de imagem/vídeo/áudio) como ImageMagick/FFmpeg.
2. **Precedente da indústria:** praticamente toda engine de jogos
   (id Tech, engines baseadas em zlib/miniz para pacotes .pak/.zip, etc.)
   embute zlib ou equivalente no runtime para descompressão de assets —
   é considerado parte do "kit básico" de um runtime, não uma dependência
   de pipeline de conteúdo.
3. **Acoplamento com o formato:** o próprio formato `game.pkg` (RFC 02)
   assume payloads comprimidos com deflate; não ter descompressão no
   runtime tornaria o formato de pacote inutilizável fora da Toolchain,
   quebrando a premissa de que o runtime "carrega e executa pacotes já
   compilados" (RFC 00).

## Consequências
- `src/pkg/` (biblioteca compartilhada entre Toolchain e runtime) linka
  zlib de forma `PRIVATE` — nenhum tipo de zlib vaza na API pública;
  consumidores de `pkg` não precisam saber que zlib existe por baixo.
- Nenhuma outra dependência de Toolchain (ImageMagick, FFmpeg) pode ser
  linkada por bibliotecas de runtime (`src/resources/`, futuros
  `src/render/`, etc.) — essa restrição continua valendo integralmente.
- Se no futuro o formato de payload migrar para outro esquema de
  compressão, esta decisão deve ser revisitada.
