#include <pybind11/eigen.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <Eigen/Core>
#include <memory>
#include <vector>

#include "stl_vector_eigen.h"

namespace py = pybind11;
using namespace py::literals;

PYBIND11_MAKE_OPAQUE(std::vector<Eigen::Vector3d>);

namespace vbr_devkit {
    PYBIND11_MODULE(vbr_devkit_pybind, m) {
        auto vector3dvector = pybind_eigen_vector_of_vector<Eigen::Vector3d>(
                m, "_Vector3dVector", "std::vector<Eigen::Vector3d>",
                py::py_array_to_vectors_double<Eigen::Vector3d>);
    }

}
