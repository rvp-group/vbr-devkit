import os
import sys
from pathlib import Path
import typer
from tqdm import tqdm
from typing import List


def main(input_bag_f: str, output_dir: str, size_gb: float = 5, skip_topics: List[str] = ["/imu/odometry"]):
    try:
        from rosbag import Bag
    except ModuleNotFoundError:
        print("rosbags library not installed, run 'pip install -U rosbag'")
        sys.exit(-1)

    print(f'Opening input bag: {Path(input_bag_f)}')
    input_bag = Bag(input_bag_f, 'r')

    # Get list of available topics
    input_topics = list(input_bag.get_type_and_topic_info()[1].keys())
    input_topics = list(filter(lambda x: x not in skip_topics, input_topics))
    print(f"Writing the following topics: {input_topics}")



    output_prefix = Path(input_bag_f).name.split(".")[0]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # total_size = input_bag.size
    # num_bags = int(total_size / (1024 ** 3 * size_gb)) + 1
    # print(f'Splitting {input_bag_f} in {num_bags} bags of size {size_gb} Gb')

    count = 0
    current_size = 0
    output_bag = None

    for topic, msg, t in tqdm(input_bag.read_messages(topics=input_topics, raw=True), total=input_bag.get_message_count(),
                              desc=f"Reading {input_bag_f}"):
        if output_bag is None:
            output_filename = f"{output_prefix}_{count}.bag"
            output_filename = Path(output_dir) / output_filename
            output_bag = Bag(output_filename, 'w')
            current_size = 0

        if current_size >= size_gb * 1024 ** 3:
            if output_bag is not None:
                output_bag.close()
            count += 1
            output_filename = f"{output_prefix}_{count}.bag"
            output_filename = Path(output_dir) / output_filename
            output_bag = Bag(output_filename, 'w')
            current_size = 0

        output_bag.write(topic, msg, t, raw=True)
        current_size += len(msg[1])

    if output_bag is not None:
        output_bag.close()

    input_bag.close()

    print("Success")


if __name__ == '__main__':
    typer.run(main)
