find_package(ZLIB REQUIRED)

add_library(pkg STATIC
    src/format.cpp
    src/compression.cpp
)

target_include_directories(pkg PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(pkg PUBLIC cxx_std_20)
# ZLIB fica PRIVATE: quem consome `pkg` não precisa saber que zlib existe
# por baixo (nenhum tipo de zlib vaza nos headers públicos); o CMake
# ainda propaga o link corretamente para os consumidores finais.
target_link_libraries(pkg PRIVATE ZLIB::ZLIB)
