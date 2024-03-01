from typing import Any, Union

import numpy as np
from vbr_devkit.tools.image import Image
from vbr_devkit.tools.imu import Imu
from vbr_devkit.tools.point_cloud2 import PointCloudXf

conversion_dict = {
    "sensor_msgs/msg/PointCloud2": PointCloudXf.from_ros,
    "sensor_msgs/msg/Image": Image.from_ros,
    "sensor_msgs/msg/Imu": Imu.from_ros
}


def convert_msg_to_datum(
        msg: Any,
        msg_type: str) -> Union[PointCloudXf, np.ndarray]:
    return conversion_dict[msg_type](msg)
