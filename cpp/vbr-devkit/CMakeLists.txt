cmake_minimum_required(VERSION 3.16...3.27)
project(vbr_devkit LANGUAGES CXX)

set(CMAKE_BUILD_TYPE Release)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Eigen3 REQUIRED)

add_library(${PROJECT_NAME}
        src/io/ros.cpp)

target_include_directories(include)