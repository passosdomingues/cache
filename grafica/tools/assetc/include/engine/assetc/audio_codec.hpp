#pragma once
#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace engine::assetc {

struct AudioBuffer {
    std::uint32_t sample_rate = 0;
    std::uint32_t channels = 0;
    std::uint32_t frame_count = 0;      // amostras por canal
    std::vector<std::int16_t> samples;  // intercalado (interleaved), frame_count*channels
};

struct AudioTransform {
    std::string trim_start;     // segundos, ex.: "1.5" (vazio = sem corte no inicio)
    std::string trim_duration;  // segundos, ex.: "3.0" (vazio = ate o fim)
    double fade_in = 0.0;       // segundos
    double fade_out = 0.0;      // segundos
    bool normalize = false;     // normalizacao de loudness (EBU R128, passo unico)
    std::uint32_t sample_rate = 44100;
    std::uint32_t channels = 2; // 1 = mono, 2 = estereo
};

// Decodifica e transforma um audio via FFmpeg CLI, retornando PCM s16le
// intercalado na taxa/canais pedidos. Lanca std::runtime_error se o
// FFmpeg nao estiver instalado ou se a conversao falhar.
//
// Nota sobre `normalize`: usa o filtro `loudnorm` (EBU R128) em passo
// unico — mais simples e rapido que o modo de duas passagens do FFmpeg,
// as custas de alguma precisao. Suficiente para o Sprint 5.
AudioBuffer load_and_transform_audio(const std::filesystem::path& source, const AudioTransform& transform);

} // namespace engine::assetc
