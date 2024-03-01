#!/usr/bin/python3
from tqdm import tqdm
import argparse
import os
import os.path as path
import rosbag
from ros_conversions import *
import open3d as o3d
import cv2


def convert_kitti(output_dir: str, bag: rosbag.Bag, convert_bayer=True) -> None:
    bag_info = input_bag.get_type_and_topic_info()
    topics = list(bag_info.topics.keys())
    # Create directories for every topic:
    # - remove first /
    # - replace all other / with _
    dict_topic_folders = {topic: path.join(output_dir, topic[1:].replace('/', '_').replace('_image_raw', '')) for topic
                          in topics}
    for folder in dict_topic_folders.values():
        os.makedirs(folder, exist_ok=True)

    for topic, msg, t in tqdm(bag.read_messages(), total=bag.get_message_count()):
        if 'points' in topic:
            # Handle point cloud
            cloud = ros_cloud_to_numpy(msg)
            points = np.zeros((cloud.shape[0] * cloud.shape[1], 3), dtype=np.float32)
            # print(points.shape)
            points[:, 0] = cloud['x'].flatten()
            points[:, 1] = cloud['y'].flatten()
            points[:, 2] = cloud['z'].flatten()
            # print(points)
            cloud_o3d = o3d.geometry.PointCloud()
            cloud_o3d.points = o3d.utility.Vector3dVector(points)
            # print(path.join(dict_topic_folders[topic], str(t) + '.pcd'))
            o3d.io.write_point_cloud(path.join(dict_topic_folders[topic], str(t.to_sec()) + '.pcd'), cloud_o3d)
        elif 'camera' in topic:
            # Handle image
            image = ros_image_to_numpy(msg, convert_bayer)
            cv2.imwrite(os.path.join(dict_topic_folders[topic], str(t.to_sec()) + '.png'), image)
            ...
        else:
            # ATM skip
            continue
    ...


CONVERSION_CB = {'kitti': convert_kitti}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='./convert_format --to <destination_format> --input_bag <input_bag>'
                                           ' --output_dir <output_dest>',
                                     description='Utility to convert standard ROS 1 format of VBR sequences to other '
                                                 'formats')
    parser.add_argument('--input_bag', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--to', type=str, required=True, choices=['kitti'])

    args = parser.parse_args()

    input_bag = rosbag.Bag(args.input_bag)

    if not path.isdir(args.output_dir):
        print('Creating output directory', args.output_dir)
        os.mkdir(args.output_dir)

    conversion_fn = CONVERSION_CB[args.to]

    conversion_fn(args.output_dir, input_bag)
    exit(0)
