#pragma once
#include <filesystem>
#include <string>
#include <vector>

// Utilitários internos de execução de processos externos (ImageMagick,
// FFmpeg, ...). Não faz parte da API pública do assetc_lib — por isso
// vive em src/, não em include/.
namespace engine::assetc::detail {

std::string shell_quote(const std::string& s);
bool tool_available(const std::string& name);
int run_command(const std::string& cmd);
std::vector<unsigned char> run_capture_binary(const std::string& command);
std::filesystem::path make_temp_path(const std::string& suffix);

} // namespace engine::assetc::detail
