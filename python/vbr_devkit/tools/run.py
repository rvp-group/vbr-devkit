import sys

import typer
from pathlib import Path
from rich.console import Group
from rich.panel import Panel
from rich.progress import track
from typing import Sequence
from typing_extensions import Annotated
from vbr_devkit.datasets import RosReader
from vbr_devkit.download.download_data import vbr_downloads, download_seq_fld
from vbr_devkit.datasets.convert_bag import OutputDataInterface, OutputDataInterface_lut
from vbr_devkit.tools.console import console

app = typer.Typer()


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
    str, typer.Argument(help="Name of the sequence to download", show_default=False, autocompletion=complete_sequence)],
             output_dir: Annotated[
                 Path, typer.Argument(help="Output directory. The sequence will be stored in a sub-folder",
                                      show_default=False)]) -> None:
    if sequence == "all":
        console.print(":boom: Downloading all sequences")
        console.print("[yellow] It will take a while")
        for seq in vbr_downloads:
            download_seq_fld(seq, output_dir)
    elif sequence == "train" or sequence == "test":
        console.print(f":woman_student: Downloading {sequence} sequences")
        console.print("[yellow] It will take a while")
        for seq in filter(lambda x: f"{sequence}" in x, vbr_downloads):
            download_seq_fld(seq, output_dir)
    else:
        if sequence not in vbr_downloads:
            console.log(
                f":thinking_face: Error {sequence} is not a valid sequence. Type 'vbr list' to see available sequences.")
            sys.exit(-1)
        download_seq_fld(sequence, output_dir)


@app.command(help="Convert a sequence from ROS1 to other known formats")
def convert(to: Annotated[OutputDataInterface, typer.Argument(help="Desired data format", show_default=False)],
            input_dir: Annotated[
                Path, typer.Argument(help="Input bag or directory containing multiple bags", show_default=False)],
            output_dir: Annotated[
                Path, typer.Argument(help="Output directory in which the data will be stored", show_default=False)],
            ) -> None:
    console.print(f"Converting {input_dir} to {to} format at {output_dir}")
    with RosReader(input_dir) as reader:
        with OutputDataInterface_lut[to](output_dir) as writer:
            for timestamp, topic, message in track(reader, description="Processing..."):
                writer.publish(timestamp, topic, message)
    console.print(":tada: Completed")


if __name__ == "__main__":
    app()
