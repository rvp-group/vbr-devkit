try:
    from rosbags.typesys.types import sensor_msgs__msg__Image
except ImportError as e:
    raise ImportError('rosbags library not installed, run "pip install -U rosbags"') from e

try:
    from rosbags.image import message_to_cvimage
except ImportError as e:
    raise ImportError('rosbags-image library not installed, run "pip install -U rosbags-image"') from e


class Image:
    def __init__(self):
        self.image = None
        self.encoding = None
        ...

    @staticmethod
    def from_ros(msg: sensor_msgs__msg__Image) -> "Image":
        im = Image()
        im.image = message_to_cvimage(msg)
        im.encoding = msg.encoding

        return im


