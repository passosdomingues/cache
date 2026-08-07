#include "engine/assetc/audio_codec.hpp"
#include "process_utils.hpp"

#include <cstring>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace engine::assetc {

using namespace detail;

namespace {

std::string build_filter_chain(const AudioTransform& transform) {
    std::vector<std::string> filters;

    if (!transform.trim_start.empty() || !transform.trim_duration.empty()) {
        std::string atrim = "atrim=";
        std::vector<std::string> parts;
        if (!transform.trim_start.empty()) parts.push_back("start=" + transform.trim_start);
        if (!transform.trim_duration.empty()) parts.push_back("duration=" + transform.trim_duration);
        for (std::size_t i = 0; i < parts.size(); ++i) {
            atrim += parts[i];
            if (i + 1 < parts.size()) atrim += ":";
        }
        filters.push_back(atrim);
        filters.push_back("asetpts=PTS-STARTPTS");
    }

    if (transform.fade_in > 0.0) {
        std::ostringstream f;
        f << "afade=t=in:st=0:d=" << transform.fade_in;
        filters.push_back(f.str());
    }

    if (transform.fade_out > 0.0) {
        // Fade-out independente de conhecer a duracao total: inverte o
        // audio, aplica um fade-in (que agora esta no fim original), e
        // inverte de volta.
        filters.push_back("areverse");
        std::ostringstream f;
        f << "afade=t=in:st=0:d=" << transform.fade_out;
        filters.push_back(f.str());
        filters.push_back("areverse");
    }

    if (transform.normalize) {
        filters.push_back("loudnorm");
    }

    std::string chain;
    for (std::size_t i = 0; i < filters.size(); ++i) {
        chain += filters[i];
        if (i + 1 < filters.size()) chain += ",";
    }
    return chain;
}

} // namespace

AudioBuffer load_and_transform_audio(const std::filesystem::path& source, const AudioTransform& transform) {
    if (!tool_available("ffmpeg")) {
        throw std::runtime_error(
            "FFmpeg nao encontrado (comando 'ffmpeg'). Instale com: sudo apt install ffmpeg");
    }
    if (!std::filesystem::exists(source)) {
        throw std::runtime_error("arquivo de audio nao encontrado: " + source.string());
    }
    if (transform.channels == 0) {
        throw std::runtime_error("asset de audio '" + source.string() + "': channels precisa ser >= 1");
    }

    std::string filter_chain = build_filter_chain(transform);

    std::ostringstream cmd;
    cmd << "ffmpeg -y -i " << shell_quote(source.string());
    if (!filter_chain.empty()) {
        cmd << " -af " << shell_quote(filter_chain);
    }
    cmd << " -ar " << transform.sample_rate
        << " -ac " << transform.channels
        << " -f s16le -acodec pcm_s16le pipe:1 2>/dev/null";

    auto bytes = run_capture_binary(cmd.str());
    if (bytes.empty()) {
        throw std::runtime_error("falha ao transformar audio (ffmpeg): " + source.string());
    }

    std::size_t bytes_per_frame = static_cast<std::size_t>(transform.channels) * sizeof(std::int16_t);
    if (bytes.size() % bytes_per_frame != 0) {
        throw std::runtime_error("tamanho de PCM inesperado para " + source.string());
    }

    AudioBuffer result;
    result.sample_rate = transform.sample_rate;
    result.channels = transform.channels;
    result.frame_count = static_cast<std::uint32_t>(bytes.size() / bytes_per_frame);
    result.samples.resize(bytes.size() / sizeof(std::int16_t));
    std::memcpy(result.samples.data(), bytes.data(), bytes.size());
    return result;
}

} // namespace engine::assetc
