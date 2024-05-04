add_library(vbr_devkit_core INTERFACE)

target_include_directories(vbr_devkit_core INTERFACE .)
target_link_libraries(vbr_devkit_core INTERFACE Eigen3::Eigen xtensor)
set(INCLUDE_DIRS ${PROJECT_SOURCE_DIR})
get_filename_component(INCLUDE_DIRS ${INCLUDE_DIRS} PATH)
target_include_directories(vbr_devkit_core INTERFACE ${PROJECT_SOURCE_DIR} ${INCLUDE_DIRS})

#set_global_target_properties(core)