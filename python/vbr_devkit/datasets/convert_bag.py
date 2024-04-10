import tyro
from pathlib import Path
from typing import Union
from dataclasses import dataclass
from typing_extensions import Annotated
from kitti import KittiWriter

@dataclass
class Args:
    input_dir: Path = "/"
    to = Union[
        Annotated[KittiWriter, tyro.conf.subcommand(name="kitti")]
    ]
    output_dir: Path = "/"

def main(args: Args) -> None:
    ...

def entrypoint():
    tyro.run(main)

if __name__ == "__main__":
    entrypoint()
    

