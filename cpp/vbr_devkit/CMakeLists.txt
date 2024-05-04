cmake_minimum_required(VERSION 3.16...3.27)
project(vbr_devkit_cpp LANGUAGES CXX)

option(USE_SYSTEM_EIGEN3 "Use system pre-installed Eigen" ON)
option(USE_SYSTEM_XTENSOR "Use system pre-installed xtensor" ON)
#option(USE_SYSTEM_XTENSOR-PYTHON "Use system pre-installed xtensor-python" ON)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(3rdparty/find_dependencies.cmake)
include(cmake/CompilerOptions.cmake)

add_subdirectory(core)

add_subdirectory(tests)