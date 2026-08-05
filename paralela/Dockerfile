# ═══════════════════════════════════════════════════════════════════════════════
# Stage 1 — Builder
# Compiles the simulation binary with full optimization flags.
# ═══════════════════════════════════════════════════════════════════════════════
FROM ubuntu:24.04 AS builder

LABEL maintainer="rafael"
LABEL description="AGN Parallel N-Body Simulation — MPI + C++17"

# Avoid interactive prompts during apt
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        libopenmpi-dev   \
        openmpi-bin      \
        cmake            \
        build-essential  \
        ca-certificates  \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /agn_sim

# Copy source tree
COPY CMakeLists.txt .
COPY include/       include/
COPY src/           src/

# Configure and build in Release mode
# Note: -march=native is omitted inside Docker to keep the image portable
# across hosts. If you want native optimization, add:
#   -DCMAKE_CXX_FLAGS="-march=native"
RUN cmake -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_CXX_FLAGS="-O3 -ffast-math -funroll-loops" \
    && cmake --build build -j$(nproc)

# ═══════════════════════════════════════════════════════════════════════════════
# Stage 2 — Runtime
# Minimal image with only the runtime libraries and the compiled binary.
# ═══════════════════════════════════════════════════════════════════════════════
FROM ubuntu:24.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

# Only the MPI runtime (no -dev headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libopenmpi3      \
        openmpi-bin      \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /agn_sim

# Copy compiled binary from builder stage
COPY --from=builder /agn_sim/build/agn_simulation ./build/agn_simulation

# Output directory (mounted via -v in docker run / docker-compose)
RUN mkdir -p data/output

# Default: print help. Override via `docker run ... mpirun -np 8 ./build/agn_simulation`
ENTRYPOINT ["./build/agn_simulation"]
CMD ["--help"]
