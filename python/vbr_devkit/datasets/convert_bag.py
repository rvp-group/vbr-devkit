import sys

from pathlib import Path

from vbr_devkit.datasets import KittiWriter, RosReader
import typer
from enum import Enum
from rich.progress import track
from rosbags import convert


class OutputDataInterface(str, Enum):
    kitti = "kitti",
    ros2  = "ros2",
    # Can insert additional conversion formats


OutputDataInterface_lut = {
    OutputDataInterface.kitti: KittiWriter
}

def main(to: OutputDataInterface, input_dir: Path, output_dir: Path) -> None:
    if to == OutputDataInterface.ros2:
        if not input_dir.is_dir():
            print("Processing...")
            convert.convert(input_dir, output_dir / input_dir.stem)
        else:
            for item in track(list(input_dir.iterdir()), description="Processing..."):
                if item.suffix == '.bag':
                    convert.convert(item, output_dir / item.stem)
    else:
        with RosReader(input_dir) as reader:
            with OutputDataInterface_lut[to](output_dir) as writer:
                for timestamp, topic, message in track(reader, description="Processing..."):
                    writer.publish(timestamp, topic, message)


if __name__ == "__main__":
    typer.run(main)
