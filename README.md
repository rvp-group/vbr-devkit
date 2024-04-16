<div align="center">
    <h1>VBR Development Kit</h1>
    <a href=""><img src=https://github.com/rvp-group/vbr-devkit/actions/workflows/python.yml/badge.svg /></a>
    <a href="https://pypi.org/project/vbr-devkit/"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/vbr-devkit" /></a>
    <a href=""><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/vbr-devkit" /></a>
    <br />
    <br />
    <a href="https://github.com/rvp-group/vbr-devkit"><img src="https://github.com/rvp-group/vbr-devkit/assets/5305530/f1a8d22a-af1e-42d4-b296-d94021a980cf"/></a>   
</div>
This kit contains utilities to work on the VBR SLAM dataset

# Install

```shell
pip install vbr-devkit
```

You can install autocompletion for our package by typing:

```shell
vbr --install-completion
```

you might need to restart the shell for the autocompletion to take effect.

# Usage
## Download sequences

You can list the available sequences you can download by typing:

```shell
vbr list
```
You should see something similar to this
![list](https://github.com/rvp-group/vbr-devkit/assets/5305530/c195e5b0-c5ee-4abb-a7f5-2ce97474ac4f)

After choosing your sequence, you can type

```shell
vbr download <sequence_name> <save_directory>
```

For instance, we could save `campus_train0` as follows:

```shell
vbr download campus_train0 ~/data/
```
**N.B.** The script will actually save the sequence at `<save_directory>/vbr_slam/<sequence_prefix>/<sequence_name>`. Moreover, by calling the previous command, we expect the following directory:
```
data
  - vbr_slam
    - campus
      - campus_train0
        - vbr_calib.yaml
        - campus_train0_gt.txt
        - campus_train0_00.bag
        - campus_train0_01.bag
        - campus_train0_02.bag
        - campus_train0_03.bag
        - campus_train0_04.bag                     
```

## Convert format

The sequences are provided in ROS1 format. We offer a convenient tool to change representation if you prefer working on a different format.
You can see the supported formats by typing:

```shell
vbr convert --help
```

To convert a bag or a sequence of bags, type:
```shell
vbr convert <desired_format> <input_directory/input_bag> <output_directory>
```

for instance, we could convert the `campus_train0` sequence to `kitti` format as follows:

```shell
vbr convert kitti ~/data/vbr_slam/campus/campus_train0/campus_train0_00.bag ~/data/campus_train0_00_kitti/
```

We can expect the following result:

```
data
  - campus_train0_00_kitti
    - camera_left
      - timestamps.txt
      - data
        - 0000000000.png
        - 0000000001.png
        - ...
    - camera_right
      - timestamps.txt
      - data
        - 0000000000.png
        - 0000000001.png
        - ...
    - ouster_points
      - timestamps.txt
      - data
        - .dtype.pkl
        - 0000000000.bin
        - 0000000001.bin
        - ...
    - ... 
```

**N.B.** In KITTI format, point clouds are embedded in binary files that can be opened using `Numpy` and `pickle` as follows:

```python
import numpy as np
import pickle

with open("campus_train0_00_kitti/ouster_points/data/.dtype.pkl", "rb") as f:
    cdtype = pickle.load(f)

cloud_numpy = np.fromfile("/campus_train0_00_kitti/ouster_points/data/0000000000.bin", dtype=cdtype)
```

