# syntax=docker/dockerfile:1
# Blender Compiler — imagem headless com Blender real (bpy via subprocess CLI)
# e todo o stack Python necessário para o pipeline de 8 etapas.

FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Blender (apt, universe) + Python 3.12 + ImageMagick + libs de OpenCV.
# --no-install-recommends mantém a imagem enxuta.
RUN apt-get update && apt-get install -y --no-install-recommends \
        blender \
        python3 \
        python3-pip \
        python3-venv \
        imagemagick \
        libgl1 \
        libglx0 \
        libxrender1 \
        libxi6 \
        libxfixes3 \
        libxxf86vm1 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY cli.py ./cli.py
COPY config/ ./config/

RUN mkdir -p /app/input /app/output /app/logs /app/assets

VOLUME ["/app/input", "/app/output", "/app/logs"]

RUN blender --version && python3 -c "import cv2, networkx, pydantic, typer, rich; print('deps OK')"

ENTRYPOINT ["python3", "cli.py"]
CMD ["--help"]
