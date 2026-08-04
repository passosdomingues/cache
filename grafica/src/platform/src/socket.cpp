#include "engine/platform/socket.hpp"

#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>

namespace engine::platform {

TcpSocket::~TcpSocket() { close(); }

TcpSocket::TcpSocket(TcpSocket&& other) noexcept : fd_(other.fd_) {
    other.fd_ = -1;
}

TcpSocket& TcpSocket::operator=(TcpSocket&& other) noexcept {
    if (this != &other) {
        close();
        fd_ = other.fd_;
        other.fd_ = -1;
    }
    return *this;
}

bool TcpSocket::listen(std::uint16_t port, int backlog) {
    fd_ = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd_ < 0) return false;

    int opt = 1;
    ::setsockopt(fd_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (::bind(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        close();
        return false;
    }
    if (::listen(fd_, backlog) < 0) {
        close();
        return false;
    }
    return true;
}

bool TcpSocket::accept(TcpSocket& out_client) {
    sockaddr_in client_addr{};
    socklen_t len = sizeof(client_addr);
    int client_fd = ::accept(fd_, reinterpret_cast<sockaddr*>(&client_addr), &len);
    if (client_fd < 0) return false;
    out_client.close();
    out_client.fd_ = client_fd;
    return true;
}

bool TcpSocket::connect(const std::string& host, std::uint16_t port) {
    fd_ = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd_ < 0) return false;

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);

    if (::inet_pton(AF_INET, host.c_str(), &addr.sin_addr) != 1) {
        addrinfo hints{};
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;
        addrinfo* result = nullptr;
        if (::getaddrinfo(host.c_str(), nullptr, &hints, &result) != 0 || result == nullptr) {
            close();
            return false;
        }
        addr.sin_addr = reinterpret_cast<sockaddr_in*>(result->ai_addr)->sin_addr;
        ::freeaddrinfo(result);
    }

    if (::connect(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        close();
        return false;
    }
    return true;
}

int TcpSocket::send(const void* data, std::size_t size) {
    if (fd_ < 0) return -1;
    return static_cast<int>(::send(fd_, data, size, 0));
}

int TcpSocket::receive(void* buffer, std::size_t size) {
    if (fd_ < 0) return -1;
    return static_cast<int>(::recv(fd_, buffer, size, 0));
}

void TcpSocket::close() {
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
}

} // namespace engine::platform
