add_library(core INTERFACE)
add_library(vbr_devkit::core ALIAS core)

target_include_directories(core INTERFACE .)
target_link_libraries(core INTERFACE Eigen3::Eigen xtensor)
set(INCLUDE_DIRS ${PROJECT_SOURCE_DIR})
get_filename_component(INCLUDE_DIRS ${INCLUDE_DIRS} PATH)
target_include_directories(core INTERFACE ${PROJECT_SOURCE_DIR} ${INCLUDE_DIRS})

#set_global_target_properties(core)