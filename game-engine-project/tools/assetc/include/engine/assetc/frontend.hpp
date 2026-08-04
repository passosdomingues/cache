#pragma once
#include "engine/assetc/asset_ir.hpp"
#include "engine/assetc/asset_manifest.hpp"

#include <functional>
#include <string>
#include <unordered_map>

namespace engine::assetc {

// Front-end: traduz um SourceAsset em um nó de Asset IR. Cada tipo de
// asset (raw, image, audio, ...) tem seu próprio front-end — o núcleo do
// compilador nunca decide política de runtime, só produz IR (RFC 02).
using FrontendFn = std::function<AssetIRNode(const SourceAsset&)>;

// `version` entra na chave de cache: incrementar quando a lógica de
// compilação de um tipo mudar invalida o cache de todos os assets desse
// tipo, mesmo que o arquivo fonte não tenha mudado.
struct FrontendInfo {
    FrontendFn compile;
    int version = 1;
};

class FrontendRegistry {
public:
    static FrontendRegistry& instance();

    void register_frontend(const std::string& type, FrontendInfo info);
    const FrontendInfo* find(const std::string& type) const;

private:
    FrontendRegistry();
    std::unordered_map<std::string, FrontendInfo> frontends_;
};

} // namespace engine::assetc
