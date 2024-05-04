//
// Created by eg on 04/05/24.
//
#include "project_cloud.hpp"
#include <iostream>
#include <xtensor/xarray.hpp>
#include <xtensor/xio.hpp>
#include <xtensor/xrandom.hpp>
#include <xtensor/xadapt.hpp>

int main(int argc, char **argv) {
    xt::xtensor<double, 2> pcd = xt::random::rand<double>({128 * 1024, 3}, -60, 60);
    xt::view(pcd, xt::all(), 2) /= 10;

    std::cout << "PCD=\n" << pcd << std::endl;

    xt::xtensor<bool, 1> valid_mask;
    xt::xtensor<double, 3> xy_residuals;
    const auto lut = vbr_devkit::projectSphericalLUT<double>(pcd, M_PI_2, 2 * M_PI, 128, 1024, valid_mask,
                                                             xy_residuals);

    const auto res = xt::where(lut > -1);
    for (size_t i = 0; i < res[0].size(); ++i) {
        const auto &r = res[0][i];
        const auto &c = res[1][i];
        std::cout << "lut(" + std::to_string(r) + ", " + std::to_string(c) + ")= " << lut(r, c) << std::endl;
    }

    return 0;
}