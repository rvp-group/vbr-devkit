#!/usr/bin/python3
import argparse
import time
from typing import Any, Generator

from numpy import ndarray
from tqdm import tqdm
import os
import os.path as path
import open3d as o3d
import numpy as np
import cv2
from utils import (
    read_intrinsics,
    read_extrinsics
)


def project_cloud(filename: str, K: np.float32, dist_coeffs: np.float32, image_size: (int, int),
                  cam_T_cloud: np.float32, max_depth: float = 60.0) -> np.ndarray:
    pcd: o3d.geometry.PointCloud = o3d.io.read_point_cloud(filename)
    pcd.transform(cam_T_cloud)
    points = np.asarray(pcd.points)
    # Keep only points that are in front of the camera
    points = points[points[:, 2] > 0]
    depths = points[:, 2]
    img_points, _ = cv2.projectPoints(points, np.zeros((3,)), np.zeros((3,)), K, dist_coeffs)
    img_points = img_points.reshape((-1, 2))
    valid_mask = (0 <= img_points[:, 0]) & \
                 (img_points[:, 0] < image_size[0]) & \
                 (0 <= img_points[:, 1]) & \
                 (img_points[:, 1] < image_size[1])
    img_points = img_points[valid_mask]
    depths = depths[valid_mask]

    output = np.zeros((image_size[1], image_size[0]), dtype=np.float32)
    indices = img_points.astype(np.int32)

    output[indices[:, 1], indices[:, 0]] = depths
    # Discard points with depth greater than max_distance
    output[output > max_depth] = 0.0

    return output


def save_projection_rgb(filename: str, proj_cloud: np.ndarray, max_depth: float, filename_rgb: str):
    proj_img = (proj_cloud / max_depth * 255.).astype(np.uint8)
    rgb_image = cv2.imread(filename_rgb)
    rgb_image[proj_img > 0] = np.uint8([0, 0, 255])

    cv2.imwrite(path.splitext(filename)[0] + '.jpg', rgb_image)

def save_projection(filename: str, proj_cloud: np.ndarray, save_numpy: bool, depth_scale: int):
    proj_img = (depth_scale * proj_cloud).astype(np.uint16)

    cv2.imwrite(os.path.splitext(filename)[0] + '.tiff', proj_img)
    if save_numpy:
        np.save(os.path.splitext(filename)[0] + '.npy', proj_cloud)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='./project_pointcloud --input-dir <input_dir> --output-dir <output_dir> '
                                           '--intrinsics <intrinsics.[yaml|json]> --extrinsics <extrinsics.['
                                           'yaml|json]>',
                                     description='Utility to project one or more PCD files to one or more image '
                                                 'planes defined by a camera intrinsics')
    parser.add_argument('--input-dir', type=str, required=True)
    parser.add_argument('--output-dir', type=str, required=True)
    parser.add_argument('--input-rgb-dir', type=str, required=False,
                        help='If set, the script produces a new folder <output_dir>_rgb that contains RGB images with '
                             'reprojected points.')
    parser.add_argument('--intrinsics', type=str, required=True)
    parser.add_argument('--quaternion-format', type=str, default='xyzw', choices=['xyzw', 'wxyz'], required=False)
    parser.add_argument('--extrinsics', type=str, required=True, help='SE(3) Transform from PointCloud reference '
                                                                      'frame to camera optical frame '
                                                                      '(p_cam = T_extrinsic * p_cloud)')
    parser.add_argument('--save-numpy', action='store_true', required=False)
    parser.add_argument('--depth-scale', type=int, default=1000, required=False,
                        help='Scaling value "S" applied during the projection of the cloud.'
                             ' (proj(x,y)<uint16> = (S * depth(x,y)<float>).cast<uint16>')
    parser.add_argument('--max-depth', type=float, default=60.0, required=False)
    args = parser.parse_args()

    K, dist_coeffs, image_size = read_intrinsics(args.intrinsics)
    cam_T_cloud = read_extrinsics(args.extrinsics, args.quaternion_format)

    if not path.isdir(args.output_dir):
        print('Creating output directory', args.output_dir)
        os.mkdir(args.output_dir)

    input_cloud_files = [f for f in os.listdir(args.input_dir) if path.isfile(path.join(args.input_dir, f))]
    input_cloud_files.sort()
    projected_clouds = (
        project_cloud(path.join(args.input_dir, f), K, dist_coeffs, image_size, cam_T_cloud, args.max_depth) for f in
        tqdm(input_cloud_files, 'Projecting Clouds'))
    input_rgb_files = None
    output_rgb_dir = None
    input_rgb_files_wno_extension = None
    if args.input_rgb_dir is not None:
        input_rgb_files = [f for f in os.listdir(args.input_rgb_dir) if path.isfile(path.join(args.input_rgb_dir, f))]
        input_rgb_files_wno_extension = [path.splitext(f)[0] for f in input_rgb_files]
        output_rgb_dir = args.output_dir + "_rgb"
        if not path.isdir(output_rgb_dir):
            print('Creating output rgb directory', output_rgb_dir)
            os.mkdir(output_rgb_dir)

    for proj, filename in zip(projected_clouds, input_cloud_files):
        save_projection(path.join(args.output_dir, filename), proj, args.save_numpy, args.depth_scale)
        if input_rgb_files is not None:
            # print('Input RGB directory:', args.input_rgb_dir)
            # print('Input RGB files:', input_rgb_files)
            # print('Output RGB directory:', output_rgb_dir)
            # print('Filename:', filename)
            # Find corresponding RGB image given 'filename'
            rgb_name_wno_extension = path.splitext(filename)[0]
            if rgb_name_wno_extension in input_rgb_files_wno_extension:
                rgb_filename_index = input_rgb_files_wno_extension.index(rgb_name_wno_extension)
                rgb_filename = path.join(args.input_rgb_dir, input_rgb_files[rgb_filename_index])
                save_projection_rgb(path.join(output_rgb_dir, filename), proj, args.max_depth, rgb_filename)
    exit(0)
