#include "engine/assetc/frontend.hpp"
#include "engine/assetc/atlas_packer.hpp"
#include "engine/assetc/audio_codec.hpp"
#include "engine/assetc/image_codec.hpp"
#include "engine/pkg/compression.hpp"
#include "engine/platform/filesystem.hpp"

#include <cstring>
#include <stdexcept>

namespace engine::assetc {

namespace {

void append_u32(std::vector<unsigned char>& out, std::uint32_t value) {
    const auto* bytes = reinterpret_cast<const unsigned char*>(&value);
    out.insert(out.end(), bytes, bytes + sizeof(value));
}

void blit(ImageBuffer& dst, const ImageBuffer& src, std::uint32_t x, std::uint32_t y) {
    for (std::uint32_t row = 0; row < src.height; ++row) {
        const unsigned char* src_row = &src.pixels[static_cast<std::size_t>(row) * src.width * src.channels];
        unsigned char* dst_row =
            &dst.pixels[(static_cast<std::size_t>(y + row) * dst.width + x) * dst.channels];
        std::memcpy(dst_row, src_row, static_cast<std::size_t>(src.width) * src.channels);
    }
}

// --- front-end "raw" (Sprint 3): copia o arquivo fonte sem transformação ---
AssetIRNode compile_raw(const SourceAsset& asset, const FrontendContext& /*context*/) {
    if (asset.source_path.empty()) {
        throw std::runtime_error("asset '" + asset.id + "' (type=raw): campo 'path' obrigatorio");
    }
    auto content = platform::fs::read_text_file(asset.source_path);
    if (!content) {
        throw std::runtime_error("asset '" + asset.id + "': nao foi possivel ler " + asset.source_path.string());
    }
    AssetIRNode node;
    node.id = asset.id;
    node.type = asset.type;
    node.source_path = asset.source_path.string();
    node.dependencies = asset.dependencies;
    node.payload.assign(content->begin(), content->end());
    return node;
}

// --- front-end "image" (Sprint 4): ImageMagick -> RGBA8 -> mipmaps -> deflate ---
AssetIRNode compile_image(const SourceAsset& asset, const FrontendContext& /*context*/) {
    if (asset.source_path.empty()) {
        throw std::runtime_error("asset '" + asset.id + "' (type=image): campo 'path' obrigatorio");
    }

    ImageTransform transform;
    transform.resize = asset.param("resize");
    transform.crop = asset.param("crop");
    transform.pad = static_cast<unsigned>(std::stoul(asset.param("pad", "0")));

    ImageBuffer base = load_and_transform_image(asset.source_path, transform);

    unsigned max_mips = static_cast<unsigned>(std::stoul(asset.param("mips", "0")));
    auto mips = generate_mipmaps(base, max_mips);

    // Payload nao-comprimido: [u32 mip_count] + por nivel [u32 w][u32 h][pixels RGBA8]
    std::vector<unsigned char> raw;
    append_u32(raw, static_cast<std::uint32_t>(mips.size()));
    for (const auto& level : mips) {
        append_u32(raw, level.width);
        append_u32(raw, level.height);
        raw.insert(raw.end(), level.pixels.begin(), level.pixels.end());
    }

    AssetIRNode node;
    node.id = asset.id;
    node.type = asset.type;
    node.source_path = asset.source_path.string();
    node.dependencies = asset.dependencies;
    node.metadata = {
        {"width", std::to_string(base.width)},
        {"height", std::to_string(base.height)},
        {"channels", std::to_string(base.channels)},
        {"mip_count", std::to_string(mips.size())},
        {"uncompressed_size", std::to_string(raw.size())},
    };
    node.payload = pkg::deflate_compress(raw);
    node.metadata.emplace_back("compressed_size", std::to_string(node.payload.size()));
    return node;
}

// --- front-end "atlas"/Sprite Compiler (Sprint 4): empacota dependências "image" ---
AssetIRNode compile_atlas(const SourceAsset& asset, const FrontendContext& context) {
    if (asset.dependencies.empty()) {
        throw std::runtime_error("asset '" + asset.id + "' (type=atlas): precisa de ao menos uma dependencia");
    }

    std::uint32_t max_width = static_cast<std::uint32_t>(std::stoul(asset.param("max_width", "1024")));
    std::uint32_t padding = static_cast<std::uint32_t>(std::stoul(asset.param("padding", "2")));
    unsigned max_mips = static_cast<unsigned>(std::stoul(asset.param("mips", "0")));

    std::vector<SpriteInput> sprite_inputs;
    std::vector<ImageBuffer> sprite_images;
    sprite_inputs.reserve(asset.dependencies.size());
    sprite_images.reserve(asset.dependencies.size());

    for (const auto& dep_id : asset.dependencies) {
        const AssetIRNode* dep = context.find(dep_id);
        if (!dep) {
            throw std::runtime_error("atlas '" + asset.id + "': dependencia nao compilada: " + dep_id);
        }

        std::uint32_t w = static_cast<std::uint32_t>(std::stoul(dep->get("width", "0")));
        std::uint32_t h = static_cast<std::uint32_t>(std::stoul(dep->get("height", "0")));
        std::uint32_t uncompressed_size = static_cast<std::uint32_t>(std::stoul(dep->get("uncompressed_size", "0")));
        if (w == 0 || h == 0) {
            throw std::runtime_error("atlas '" + asset.id + "': dependencia '" + dep_id +
                                      "' nao parece ser uma imagem valida (use type=image)");
        }

        auto decoded = pkg::inflate_decompress(dep->payload, uncompressed_size);
        // Layout do payload de uma imagem: [u32 mip_count][u32 w][u32 h][pixels do mip 0]...
        std::uint32_t mip0_w = 0, mip0_h = 0;
        std::memcpy(&mip0_w, decoded.data() + 4, sizeof(mip0_w));
        std::memcpy(&mip0_h, decoded.data() + 8, sizeof(mip0_h));

        ImageBuffer sprite;
        sprite.width = mip0_w;
        sprite.height = mip0_h;
        sprite.channels = 4;
        sprite.pixels.assign(decoded.begin() + 12,
                              decoded.begin() + 12 + static_cast<std::ptrdiff_t>(mip0_w) * mip0_h * 4);

        sprite_inputs.push_back(SpriteInput{dep_id, sprite.width, sprite.height});
        sprite_images.push_back(std::move(sprite));
    }

    AtlasLayout layout = pack_shelves(sprite_inputs, max_width, padding);

    ImageBuffer atlas;
    atlas.width = layout.width;
    atlas.height = layout.height;
    atlas.channels = 4;
    atlas.pixels.assign(static_cast<std::size_t>(atlas.width) * atlas.height * 4, 0);

    for (std::size_t i = 0; i < sprite_images.size(); ++i) {
        const auto& placement = layout.placements[i];
        blit(atlas, sprite_images[i], placement.x, placement.y);
    }

    auto mips = generate_mipmaps(atlas, max_mips);

    // Payload nao-comprimido:
    //   [u32 atlas_w][u32 atlas_h][u32 mip_count][u32 sprite_count]
    //   por sprite: [u32 id_len][id][u32 x][u32 y][u32 w][u32 h]
    //   por nivel de mip: pixels RGBA8
    std::vector<unsigned char> raw;
    append_u32(raw, atlas.width);
    append_u32(raw, atlas.height);
    append_u32(raw, static_cast<std::uint32_t>(mips.size()));
    append_u32(raw, static_cast<std::uint32_t>(layout.placements.size()));
    for (const auto& placement : layout.placements) {
        append_u32(raw, static_cast<std::uint32_t>(placement.id.size()));
        raw.insert(raw.end(), placement.id.begin(), placement.id.end());
        append_u32(raw, placement.x);
        append_u32(raw, placement.y);
        append_u32(raw, placement.width);
        append_u32(raw, placement.height);
    }
    for (const auto& level : mips) {
        raw.insert(raw.end(), level.pixels.begin(), level.pixels.end());
    }

    AssetIRNode node;
    node.id = asset.id;
    node.type = asset.type;
    node.source_path = "";
    node.dependencies = asset.dependencies;
    node.metadata = {
        {"width", std::to_string(atlas.width)},
        {"height", std::to_string(atlas.height)},
        {"channels", "4"},
        {"mip_count", std::to_string(mips.size())},
        {"sprite_count", std::to_string(layout.placements.size())},
        {"uncompressed_size", std::to_string(raw.size())},
    };
    node.payload = pkg::deflate_compress(raw);
    node.metadata.emplace_back("compressed_size", std::to_string(node.payload.size()));
    return node;
}

// --- front-end "audio" (Sprint 5): FFmpeg -> PCM s16le -> deflate ---
AssetIRNode compile_audio(const SourceAsset& asset, const FrontendContext& /*context*/) {
    if (asset.source_path.empty()) {
        throw std::runtime_error("asset '" + asset.id + "' (type=audio): campo 'path' obrigatorio");
    }

    AudioTransform transform;
    transform.trim_start = asset.param("trim_start");
    transform.trim_duration = asset.param("trim_duration");
    transform.fade_in = std::stod(asset.param("fade_in", "0"));
    transform.fade_out = std::stod(asset.param("fade_out", "0"));
    transform.normalize = asset.param("normalize", "false") == "true";
    transform.sample_rate = static_cast<std::uint32_t>(std::stoul(asset.param("sample_rate", "44100")));
    transform.channels = static_cast<std::uint32_t>(std::stoul(asset.param("channels", "2")));

    AudioBuffer audio = load_and_transform_audio(asset.source_path, transform);

    bool loop = asset.param("loop", "false") == "true";

    // Payload nao-comprimido: [u32 sample_rate][u32 channels][u32 frame_count][amostras s16le intercaladas]
    std::vector<unsigned char> raw;
    append_u32(raw, audio.sample_rate);
    append_u32(raw, audio.channels);
    append_u32(raw, audio.frame_count);
    std::size_t samples_bytes = audio.samples.size() * sizeof(std::int16_t);
    std::size_t header_size = raw.size();
    raw.resize(header_size + samples_bytes);
    if (samples_bytes > 0) {
        std::memcpy(raw.data() + header_size, audio.samples.data(), samples_bytes);
    }

    double duration = (audio.channels > 0 && audio.sample_rate > 0)
        ? static_cast<double>(audio.frame_count) / static_cast<double>(audio.sample_rate)
        : 0.0;

    AssetIRNode node;
    node.id = asset.id;
    node.type = asset.type;
    node.source_path = asset.source_path.string();
    node.dependencies = asset.dependencies;
    node.metadata = {
        {"sample_rate", std::to_string(audio.sample_rate)},
        {"channels", std::to_string(audio.channels)},
        {"frame_count", std::to_string(audio.frame_count)},
        {"duration_seconds", std::to_string(duration)},
        {"loop", loop ? "true" : "false"},
        {"uncompressed_size", std::to_string(raw.size())},
    };
    node.payload = pkg::deflate_compress(raw);
    node.metadata.emplace_back("compressed_size", std::to_string(node.payload.size()));
    return node;
}

} // namespace

FrontendRegistry& FrontendRegistry::instance() {
    static FrontendRegistry registry;
    return registry;
}

FrontendRegistry::FrontendRegistry() {
    // Front-end "raw" (Sprint 3): copia o arquivo fonte para o IR sem
    // transformação.
    register_frontend("raw", FrontendInfo{compile_raw, 1});
    // Front-end "image" (Sprint 4): decodifica/transforma via ImageMagick,
    // gera mipmaps e comprime o payload final.
    register_frontend("image", FrontendInfo{compile_image, 1});
    // Front-end "atlas" (Sprint 4, Sprite Compiler): empacota dependências
    // "image" já compiladas em um único atlas, com tabela de sprites.
    register_frontend("atlas", FrontendInfo{compile_atlas, 1});
    // Front-end "audio" (Sprint 5): decodifica/transforma via FFmpeg
    // (trim, fade in/out, normalize) e comprime o payload final.
    register_frontend("audio", FrontendInfo{compile_audio, 1});
}

void FrontendRegistry::register_frontend(const std::string& type, FrontendInfo info) {
    frontends_[type] = std::move(info);
}

const FrontendInfo* FrontendRegistry::find(const std::string& type) const {
    auto it = frontends_.find(type);
    return it == frontends_.end() ? nullptr : &it->second;
}

} // namespace engine::assetc
