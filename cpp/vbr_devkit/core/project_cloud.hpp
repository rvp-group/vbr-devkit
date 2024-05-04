//
// Created by eg on 27/03/24.
//

#pragma once

#include "types.h"
#include <xtensor/xarray.hpp>
#include <xtensor/xtensor.hpp>

namespace vbr_devkit {

    template<typename T>
    xt::xtensor<IndexType, 2> projectSphericalLUT(const xt::xtensor<T, 2> &pcd,
                                                  const float vfov,
                                                  const float hfov,
                                                  const unsigned int image_rows,
                                                  const unsigned int image_cols,
                                                  xt::xtensor<bool, 1> &valid_mask,
                                                  xt::xtensor<double, 3> &xy_residuals,
                                                  const float min_range = 0.1,
                                                  const float max_range = 120) {
        const float fx = -(float) image_cols / hfov;
        const float fy = -(float) image_rows / vfov;
        const float cx = (float) image_cols / 2;
        const float cy = (float) image_rows / 2;
        valid_mask.resize({pcd.shape(0)});
        valid_mask *= false;

        std::array<size_t, 2> lut_shape = {image_rows, image_cols};
        xt::xtensor<IndexType, 2> lut = xt::ones<IndexType>(lut_shape);
        lut *= -1;
        xy_residuals = xt::zeros<double>(xt::xtensor<double, 3>::shape_type({image_rows, image_cols, 2}));


        for (unsigned long long i = 0; i < pcd.shape(0); ++i) {
            const auto &x = pcd(i, 0);
            const auto &y = pcd(i, 1);
            const auto &z = pcd(i, 2);
            const auto range = sqrt(x * x + y * y + z * z);

            if (range < min_range or range > max_range) continue;

            const double az = atan2(y, x);
            const double el = atan2(z, sqrt(x * x + y * y));

            const auto u = fx * az + cx; // col
            const auto v = fy * el + cy; // row

            const auto iu = (int) round(u);
            const auto iv = (int) round(v);

            if (iv < 0 or iv >= (int) image_rows or iu < 0 or iu >= (int) image_cols)
                continue;

            // Z-Buffer
            if (lut(iv, iu) != -1) {
                const auto j = lut(iv, iu);
                const auto jrange = sqrt(pcd(j, 0) * pcd(j, 0) +
                                         pcd(j, 1) * pcd(j, 1) +
                                         pcd(j, 2) * pcd(j, 2));
                if (range >= jrange) continue;

                // If range < jrange then invalidate j
                valid_mask(j) = false;
            }
            valid_mask(i) = true;
            xy_residuals(iv, iu, 0) = (double) iu - u;
            xy_residuals(iv, iu, 1) = (double) iv - v;
            lut(iv, iu) = (IndexType) i;
        }
        return lut;
    }
}