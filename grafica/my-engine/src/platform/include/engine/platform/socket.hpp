#pragma once
#include <cstddef>
#include <cstdint>
#include <string>

namespace engine::platform {

// Abstração mínima de socket TCP para Linux (RFC 05 — Plataformas).
// Suficiente para o Sprint 1; Asset Server e distribuição de pacotes
// (Sprint 21) vão precisar de mais robustez (timeouts, non-blocking).
class TcpSocket {
public:
    TcpSocket() = default;
    ~TcpSocket();

    TcpSocket(const TcpSocket&) = delete;
    TcpSocket& operator=(const TcpSocket&) = delete;
    TcpSocket(TcpSocket&& other) noexcept;
    TcpSocket& operator=(TcpSocket&& other) noexcept;

    bool listen(std::uint16_t port, int backlog = 16);
    bool accept(TcpSocket& out_client);
    bool connect(const std::string& host, std::uint16_t port);

    int send(const void* data, std::size_t size);
    int receive(void* buffer, std::size_t size);

    void close();
    bool is_valid() const { return fd_ >= 0; }

private:
    int fd_ = -1;
};

} // namespace engine::platform
