//
// Created by eg on 04/05/24.
//

#include "core/project_cloud.hpp"
#include <pybind11/pybind11.h>

#include <xtensor-python/pytensor.hpp>

PYBIND11_MODULE(vbr_devkit_pybind, m) {
    xt::import_numpy();
    m.def("project_spherical_lut", &vbr_devkit::projectSphericalLUT<double>);
}

