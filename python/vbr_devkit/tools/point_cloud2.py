import sys
from typing import Iterable, List, Optional

import numpy as np

try:
    from rosbags.typesys.stores.ros1_noetic import (
        sensor_msgs__msg__PointCloud2 as PointCloud2,
        sensor_msgs__msg__PointField as PointField,
    )

except ImportError as e:
    raise ImportError('rosbags library not installed, run "pip install -U rosbags"') from e

_DATATYPES = {}
_DATATYPES[PointField.INT8] = np.dtype(np.int8)
_DATATYPES[PointField.UINT8] = np.dtype(np.uint8)
_DATATYPES[PointField.INT16] = np.dtype(np.int16)
_DATATYPES[PointField.UINT16] = np.dtype(np.uint16)
_DATATYPES[PointField.INT32] = np.dtype(np.int32)
_DATATYPES[PointField.UINT32] = np.dtype(np.uint32)
_DATATYPES[PointField.FLOAT32] = np.dtype(np.float32)
_DATATYPES[PointField.FLOAT64] = np.dtype(np.float64)

DUMMY_FIELD_PREFIX = "unnamed_field"


class PointCloudXf:
    def __init__(self):
        self.fields: List[PointField] = []
        self.points: np.ndarray[None, np.dtype[np.float32]] = np.zeros(0)
        ...

    @staticmethod
    def from_ros(msg: PointCloud2):
        cloud = PointCloudXf()
        cloud.fields = msg.fields
        field_names = [f.name for f in msg.fields]
        cloud.points = read_points(msg, field_names)

        return cloud


def read_points(
        cloud: PointCloud2,
        field_names: Optional[List[str]] = None,
        uvs: Optional[Iterable] = None,
        reshape_organized_cloud: bool = False,
) -> np.ndarray:
    """
    Read points from a sensor_msgs.PointCloud2 message.
    :param cloud: The point cloud to read from sensor_msgs.PointCloud2.
    :param field_names: The names of fields to read. If None, read all fields.
                        (Type: Iterable, Default: None)
    :param uvs: If specified, then only return the points at the given
        coordinates. (Type: Iterable, Default: None)
    :param reshape_organized_cloud: Returns the array as an 2D organized point cloud if set.
    :return: Structured NumPy array containing all points.
    """
    # Cast bytes to numpy array
    points = np.ndarray(
        shape=(cloud.width * cloud.height,),
        dtype=dtype_from_fields(cloud.fields, point_step=cloud.point_step),
        buffer=cloud.data,
    )

    # Keep only the requested fields
    if field_names is not None:
        assert all(
            field_name in points.dtype.names for field_name in field_names
        ), "Requests field is not in the fields of the PointCloud!"
        # Mask fields
        points = points[list(field_names)]

    # Swap array if byte order does not match
    if bool(sys.byteorder != "little") != bool(cloud.is_bigendian):
        points = points.byteswap(inplace=True)

    # Select points indexed by the uvs field
    if uvs is not None:
        # Don't convert to numpy array if it is already one
        if not isinstance(uvs, np.ndarray):
            uvs = np.fromiter(uvs, int)
        # Index requested points
        points = points[uvs]

    # Cast into 2d array if cloud is 'organized'
    if reshape_organized_cloud and cloud.height > 1:
        points = points.reshape(cloud.width, cloud.height)

    return points


def dtype_from_fields(fields: Iterable[PointField], point_step: Optional[int] = None) -> np.dtype:
    """
    Convert a Iterable of sensor_msgs.msg.PointField messages to a np.dtype.
    :param fields: The point cloud fields.
                   (Type: iterable of sensor_msgs.msg.PointField)
    :param point_step: Point step size in bytes. Calculated from the given fields by default.
                       (Type: optional of integer)
    :returns: NumPy datatype
    """
    # Create a lists containing the names, offsets and datatypes of all fields
    field_names = []
    field_offsets = []
    field_datatypes = []
    for i, field in enumerate(fields):
        # Datatype as numpy datatype
        datatype = _DATATYPES[field.datatype]
        # Name field
        if field.name == "":
            name = f"{DUMMY_FIELD_PREFIX}_{i}"
        else:
            name = field.name
        # Handle fields with count > 1 by creating subfields with a suffix consiting
        # of "_" followed by the subfield counter [0 -> (count - 1)]
        assert field.count > 0, "Can't process fields with count = 0."
        for a in range(field.count):
            # Add suffix if we have multiple subfields
            if field.count > 1:
                subfield_name = f"{name}_{a}"
            else:
                subfield_name = name
            assert subfield_name not in field_names, "Duplicate field names are not allowed!"
            field_names.append(subfield_name)
            # Create new offset that includes subfields
            field_offsets.append(field.offset + a * datatype.itemsize)
            field_datatypes.append(datatype.str)

    # Create dtype
    dtype_dict = {"names": field_names, "formats": field_datatypes, "offsets": field_offsets}
    if point_step is not None:
        dtype_dict["itemsize"] = point_step
    return np.dtype(dtype_dict)
