import sys

import typer
from pathlib import Path
from rich.console import Group
from rich.panel import Panel
from rich.progress import track
from typing import List, Optional, Sequence
from typing_extensions import Annotated
from vbr_devkit.datasets import RosReader
from vbr_devkit.download.download_data import vbr_downloads, download_sequences
from vbr_devkit.download.registry import FileKind, resolve_sequences
from vbr_devkit.datasets.convert_bag import OutputDataInterface, OutputDataInterface_lut
from vbr_devkit.tools.console import console
from vbr_devkit.tools.update_check import installed_version, warn_if_outdated
from rosbags import convert as rosconvert

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"vbr-devkit {installed_version()}")
        warn_if_outdated()
        raise typer.Exit()


@app.callback()
def main(version: Annotated[
    Optional[bool], typer.Option("--version", "-V", help="Show the installed version and exit.",
                                 callback=_version_callback, is_eager=True)] = None) -> None:
    """Development kit for the VBR SLAM dataset."""
    warn_if_outdated()


@app.command("list",
             help="List all available VBR sequences")
def list_sequences() -> None:
    panel_group = Group(
        Panel("\n".join(["all", "train", "test"]), title="Meta"),
        Panel("\n".join([x for x in vbr_downloads if "train" in x]), title="Train"),
        Panel("\n".join([x for x in vbr_downloads if "test" in x]), title="Test")
    )
    console.print(panel_group)


def complete_sequence(incomplete: str) -> Sequence[str]:
    for seq in ["all", "train", "test"] + vbr_downloads:
        if seq.startswith(incomplete):
            yield seq


@app.command(help="Download one or more VBR sequences. Type 'vbr list' to see the available sequences.")
def download(sequence: Annotated[
    str, typer.Argument(help="Name of the sequence to download, or 'all', 'train', 'test'", show_default=False,
                        autocompletion=complete_sequence)],
             output_dir: Annotated[
                 Path, typer.Argument(help="Output directory. Files are stored in <output_dir>/vbr_slam/<location>/<sequence>/",
                                      show_default=False)],
             only: Annotated[
                 Optional[List[FileKind]], typer.Option(
                     help="Download only these file kinds (repeatable): calib, gt, bags. Default: everything.",
                     show_default=False)] = None,
             skip_existing: Annotated[
                 bool, typer.Option(help="Skip files already present with the expected size.")] = True,
             verify: Annotated[
                 bool, typer.Option(help="Verify SHA-256 checksums of downloaded files, when available.")] = True,
             dry_run: Annotated[
                 bool, typer.Option(help="Only show what would be downloaded.")] = False) -> None:
    try:
        seqs = resolve_sequences(sequence)
    except KeyError:
        console.log(
            f":thinking_face: Error {sequence} is not a valid sequence. Type 'vbr list' to see available sequences.")
        sys.exit(-1)
    if len(seqs) > 1:
        console.print(f":package: Downloading {len(seqs)} sequences ({sequence})")
        console.print("[yellow] It will take a while")
    failed = download_sequences(seqs, output_dir, kinds=only, skip_existing=skip_existing, verify=verify,
                                dry_run=dry_run)
    if failed:
        sys.exit(1)


@app.command(help="Convert a sequence from ROS1 to other known formats")
def convert(to: Annotated[OutputDataInterface, typer.Argument(help="Desired data format", show_default=False)],
            input_dir: Annotated[
                Path, typer.Argument(help="Input bag or directory containing multiple bags", show_default=False)],
            output_dir: Annotated[
                Path, typer.Argument(help="Output directory in which the data will be stored", show_default=False)],
            rgb_conversion: Annotated[
                bool, typer.Option(
                    help="Enable BayerRG8->RGB conversion during conversion in KITTI format."
                         " Disable this flag to reduce the memory footprint of the converted folder.",
                    show_default=True)] = True,
            reduce_pcloud: Annotated[
                bool, typer.Option(
                    help="Preserve only <x,y,z,intensity> channels during PointCloud conversion in KITTI format. "
                         "Allows compatibility with KITTI readers but removes extra LiDAR channels",
                    show_default=True)] = True) -> None:
    console.print(f"Converting {input_dir} to {to} format at {output_dir}")
    if to == OutputDataInterface.ros2:
        print("Processing...")
        rosconvert.convert(
            sorted([f for f in input_dir.glob("*.bag")]) if input_dir.is_dir() else [input_dir],
            output_dir / input_dir.stem,
            dst_version=None,
            compress=None,
            compress_mode="file",
            default_typestore=None,
            typestore=None,
            exclude_topics=[],
            include_topics=[],
            exclude_msgtypes=[],
            include_msgtypes=[]
        )
    else:
        with RosReader(input_dir) as reader:
            with OutputDataInterface_lut[to](output_dir, rgb_convert=rgb_conversion,
                                             pcloud_kitti_format=reduce_pcloud) as writer:
                for timestamp, topic, message in track(reader, description="Processing..."):
                    writer.publish(timestamp, topic, message)
    console.print(":tada: Completed")


if __name__ == "__main__":
    app()
