<div align="center">
    <h1>VBR Development Kit</h1>
    <h3>
        <a href="https://rvp-group.net/">Project Site</a> | 
        <a href="https://arxiv.org/abs/2404.11322">Preprint</a>
    </h3>
    <a href=""><img src=https://github.com/rvp-group/vbr-devkit/actions/workflows/python.yml/badge.svg /></a>
    <a href="https://pypi.org/project/vbr-devkit/"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/vbr-devkit" /></a>
    <a href=""><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/vbr-devkit" /></a>
    <a href="LICENSE"><img alt="Code license: BSD-3-Clause" src="https://img.shields.io/badge/code-BSD--3--Clause-blue" /></a>
    <a href="LICENSE-DATA.md"><img alt="Dataset license: CC BY-SA 4.0" src="https://img.shields.io/badge/dataset-CC%20BY--SA%204.0-lightgrey" /></a>
    <br />
    <br />
    <a href="https://github.com/rvp-group/vbr-devkit"><img src="https://github.com/rvp-group/vbr-devkit/assets/5305530/f1a8d22a-af1e-42d4-b296-d94021a980cf"/></a>   
</div>
This kit contains utilities to download the VBR dataset.

# Updates
 
<!-- TODO: add the month/year of the switch -->
- **Data distribution moved from anonymous FTP to HTTPS (`vbr-devkit` 1.0.0).**
  The dataset is no longer served over anonymous FTP. As a consequence,
  **versions of `vbr-devkit` older than 1.0.0 are no longer supported** and
  can no longer download the data. Please upgrade:
```shell
pip install -U vbr-devkit
vbr --help   # check that the CLI works
pip show vbr-devkit   # the installed version must be >= 1.0.0
```
 
  If you use `uvx`, run `uvx vbr-devkit@latest ...` to bypass a cached older
  version. Data you have already downloaded is not affected. See
  [Download sequences](#download-sequences) for the new options (resumable
  downloads, `--dry-run`, `--only`, `VBR_BASE_URL`).
 

# Install

```shell
pip install vbr-devkit
```

## Run without installing (uvx)

If you have [uv](https://docs.astral.sh/uv/) installed, you can run the kit without installing it into your environment:

```shell
uvx vbr-devkit list
```

`uvx` fetches the package into a temporary, isolated environment and runs it. Any `vbr` command works through the `vbr-devkit` entry point, for example:

```shell
uvx vbr-devkit download campus_train0 ~/data/
uvx vbr-devkit convert kitti <input.bag> <output_dir>
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

Files are downloaded over HTTPS from `https://www.diag.uniroma1.it/<sequence_name>/<file>`. Interrupted downloads are resumed: just run the same command again, files already present are skipped.

Useful options:

```shell
vbr download all ~/data/ --dry-run                     # list files and total size, download nothing
vbr download train ~/data/ --only calib --only gt      # only calibration and ground truth (no bags)
vbr download campus_train0 ~/data/ --no-skip-existing  # re-download everything
```

The download server can be overridden with the `VBR_BASE_URL` environment variable (e.g. for a mirror).

`vbr` checks PyPI at most once a day and prints a warning when a newer version is available. Set `VBR_NO_UPDATE_CHECK=1` to disable it.

**N.B.** The downloaded data is covered by the dataset license ([CC BY-SA 4.0](LICENSE-DATA.md)), not by the BSD-3-Clause license of this kit.

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

**N.B.** Converted data is *Adapted Material* in the sense of the dataset license: if you share it, you must credit the dataset, link the license, and indicate that the data was converted (see [License](#license)).

# License

| Component | License |
|-----------|---------|
| Source code of this repository (`vbr-devkit`) | [BSD-3-Clause](LICENSE) |
| VBR dataset (recordings, calibrations, ground truth) | [CC BY-SA 4.0](LICENSE-DATA.md) |

# Citation

If you use the VBR dataset or this kit in your work, please cite:

```bibtex
@inproceedings{brizi2024vbr,
  title     = {VBR: A Vision Benchmark in Rome},
  author    = {Brizi, Leonardo and Giacomini, Emanuele and Di Giammarino, Luca and Ferrari, Simone and Salem, Omar and De Rebotti, Lorenzo and Grisetti, Giorgio},
  booktitle = {IEEE International Conference on Robotics and Automation (ICRA)},
  year      = {2024}
}
```
