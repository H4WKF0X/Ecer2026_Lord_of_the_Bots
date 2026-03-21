cmake_minimum_required(VERSION 3.15)
project(ecer C)

set(CMAKE_C_STANDARD 11)

# ── Library ──────────────────────────────────────────
add_library(ecer_lib
    lib/src/config_parser.c
    lib/src/drive.c
    lib/src/servo.c
)

target_include_directories(ecer_lib PUBLIC lib/include)

target_link_libraries(ecer_lib PUBLIC kipr)

function(add_wombat_exe name)
    add_executable(${name} run/${name}.c)
    target_link_libraries(${name} PRIVATE ecer_lib)
endfunction()

add_wombat_exe(frodo)
