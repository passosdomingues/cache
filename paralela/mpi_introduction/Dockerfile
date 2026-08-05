FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        libopenmpi-dev openmpi-bin cmake build-essential \
        python3 python3-pip python3-matplotlib python3-numpy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY CMakeLists.txt .
COPY include/ include/
COPY src/ src/
COPY scripts/ scripts/

RUN cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j$(nproc)

FROM ubuntu:24.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        libopenmpi3 openmpi-bin python3 python3-matplotlib python3-numpy \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/build/mpi_didatico ./build/mpi_didatico
COPY --from=builder /app/scripts ./scripts

RUN mkdir -p plots data/output

CMD ["mpirun", "--allow-run-as-root", "--oversubscribe", "-np", "4", "./build/mpi_didatico", "--all"]
