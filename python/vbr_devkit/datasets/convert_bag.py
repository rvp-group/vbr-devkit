import tyro
from pathlib import Path
from typing import Union
from dataclasses import dataclass
from typing_extensions import Annotated
from kitti import KittiWriter

Commands = Union[
    Annotated[KittiWriter, tyro.conf.subcommand(name="kitti")]
]


@dataclass
class Args:
    from_dir: Path = "/"
    to = Union[
        Annotated[KittiWriter, tyro.conf.subcommand(name="kitti")]
    ]

def main(args: Args) -> None:
    

