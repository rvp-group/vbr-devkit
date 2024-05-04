cmake_minimum_required(VERSION 3.16)
project(vbr_devkit_pybind VERSION 0.0.4)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

set(PYBIND11_NEWPYTHON ON)
find_package(Python COMPONENTS Interpreter Development NumPy)
find_package(pybind11 REQUIRED CONFIG)

if (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../cpp/vbr_devkit/)
    add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../cpp/vbr_devkit ${CMAKE_CURRENT_BINARY_DIR}/vbr_devkit)
#else()
#    cmake_minimum_required(VERSION 3.16)
#    message(STATUS "Performing out-of-tree build, fetching vbr-devkit v${CMAKE_PROJECT_VERSION} Release from Github")
#    include(FetchContent)
#    FetchContent_Declare(
#            ext_vbr_devkit_core PREFIX vbr_devkit::core
#
#    )

endif ()

add_subdirectory(vbr_devkit/pybind)