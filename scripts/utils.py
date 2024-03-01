import typing

import yaml
import json
import os
from os import path
from tqdm import tqdm
import numpy as np
from pytransform3d.transformations import (
    transform_from_pq,
    check_pq
)


def read_intrinsics(file: str) -> (np.float32, np.float32, (int, int)):
    if '.yaml' in file:
        with open(file, 'r') as f:
            params = yaml.load(f, Loader=yaml.FullLoader)
    elif '.json' in file:
        with open(file, 'r') as f:
            params = json.load(f)

    K = np.eye(3, 3, dtype=np.float32)
    K[0, 0] = params['K'][0]
    K[1, 1] = params['K'][1]
    K[0, 2] = params['K'][2]
    K[1, 2] = params['K'][3]

    dist_coeffs = np.float32(params['dist_coeffs'])

    image_size = (params['image_size'][0], params['image_size'][1])

    return K, dist_coeffs, image_size


def read_extrinsics(file: str, quat_format: str = 'wxyz') -> np.float32:
    assert quat_format == 'wxyz' or quat_format == 'xyzw'

    if '.yaml' in file:
        with open(file, 'r') as f:
            params = yaml.load(f, Loader=yaml.FullLoader)
    elif '.json' in file:
        with open(file, 'r') as f:
            params = json.load(f)

    t = np.float32(params['t'])
    q = np.float32(params['q'])

    if quat_format == 'xyzw':
        q = np.float32([q[3], q[0], q[1], q[2]])

    pq = np.concatenate([t, q])

    return transform_from_pq(pq)


def read_poses(filename: str, file_format: str = 'tum', quat_format: str = 'wxyz', skip_rows: int = 1) -> typing.Dict[
    str, np.ndarray]:
    if file_format == 'tum':
        with (open(filename, 'r') as f):
            lines = f.readlines()[skip_rows:]
            ts_poses_lst = list(map((lambda line: (line.split()[0], np.asarray(line.split()[1:], dtype=np.float32))), lines))
            # Correct quaternion format
            if quat_format == 'xyzw':
                ts_poses_lst = [(ts, np.float32([pq[0], pq[1], pq[2], pq[6], pq[3], pq[4], pq[5]])) for (ts, pq) in
                                ts_poses_lst]
            return {ts: transform_from_pq(pq) for ts, pq in tqdm(ts_poses_lst, 'Processing Poses')}
    else:
        raise ValueError('Unsupported file format: ', file_format)
