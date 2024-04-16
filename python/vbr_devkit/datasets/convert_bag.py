import sys
sys.path.append("/home/eg/source/vbr-devkit/python")

from pathlib import Path

from vbr_devkit.datasets import KittiWriter, RosReader
import typer
from enum import Enum
from rich.progress import track


class OutputDataInterface(str, Enum):
    kitti = "kitti",
    # Can insert additional conversion formats


OutputDataInterface_lut = {
    OutputDataInterface.kitti: KittiWriter
}

def main(to: OutputDataInterface, input_dir: Path, output_dir: Path) -> None:
    with RosReader(input_dir) as reader:
        with OutputDataInterface_lut[to](output_dir) as writer:
            for timestamp, topic, message in track(reader, description="Processing..."):
                writer.publish(timestamp, topic, message)


if __name__ == "__main__":
    typer.run(main)
