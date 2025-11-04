import numpy as np

try:
    from rosbags.typesys.stores.ros1_noetic import (
        sensor_msgs__msg__Imu
    )
except ImportError as e:
    raise ImportError('rosbags library not installed, run "pip install -U rosbags"') from e


class Imu:
    def __init__(self):
        self.linear_acceleration = np.zeros((3,))
        self.angular_velocity = np.zeros((3,))
        self.orientation = np.float32([1.0, 0.0, 0.0, 0.0])
        self.linear_acceleration_covariance = np.zeros((9, ))
        self.angular_velocity_covariance = np.zeros((9, ))
        self.orientation_covariance = np.zeros((9, ))

    @staticmethod
    def from_ros(msg: sensor_msgs__msg__Imu) -> "Imu":
        meas = Imu()
        meas.linear_acceleration = np.float32([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z])

        meas.angular_velocity = np.float32([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z])

        meas.orientation = np.float32([
            msg.orientation.w,
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z
        ])

        meas.linear_acceleration_covariance = msg.linear_acceleration_covariance
        meas.angular_velocity_covariance = msg.angular_velocity_covariance
        meas.orientation_covariance = msg.orientation_covariance

        return meas