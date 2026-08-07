add_library(assetc_lib STATIC
    src/hash.cpp
    src/block_format.cpp
    src/asset_manifest.cpp
    src/frontend.cpp
    src/build_cache.cpp
    src/compiler.cpp
    src/process_utils.cpp
    src/image_codec.cpp
    src/audio_codec.cpp
    src/atlas_packer.cpp
)

target_include_directories(assetc_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(assetc_lib PUBLIC cxx_std_20)
target_link_libraries(assetc_lib PUBLIC platform pkg)

add_executable(assetc main.cpp)
target_link_libraries(assetc PRIVATE assetc_lib)
