import sensor_msgs.msg
from sensor_msgs.msg import (Image, PointCloud2)
from cv_bridge import CvBridge
import numpy as np
import ros_numpy


# Function to pass from a ros sensor_msgs.Image to numpy
def ros_image_to_numpy(msg: Image, convert_bayer) -> np.ndarray:
    bridge = CvBridge()
    if convert_bayer:
        return bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    else:
        return bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")


def ros_cloud_to_numpy(cloud_msg: PointCloud2) -> np.ndarray:
    cloud_msg.__class__ = sensor_msgs.msg.PointCloud2
    return ros_numpy.numpify(cloud_msg)
