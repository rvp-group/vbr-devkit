from pathlib import Path
import ftplib
import tyro
from typing import TYPE_CHECKING
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

DATASET_LINK = "151.100.59.119"
FTP_USER = "anonymous"

vbr_downloads = [
    "all",
    "campus_test0",
    "campus_test1",
    "campus_train0",
    "campus_train1",
    "ciampino_test0",
    "ciampino_test1",
    "ciampino_train0",
    "ciampino_train1",
    "colosseo_test0",
    "colosseo_train0",
    "diag_test0",
    "diag_train0",
    "pincio_test0",
    "pincio_train0",
    "spagna_test0",
    "spagna_train0",
]

if TYPE_CHECKING:
    VbrSlamCaptureName = str
else:
    VbrSlamCaptureName = tyro.extras.literal_type_from_choices(vbr_downloads)

CONSOLE = Console(width=120)
def main(
        dataset: VbrSlamCaptureName,
        save_dir: Path,
):
    CONSOLE.rule(f"[bold green] Downloading {dataset}")
    if dataset == "all":
        for seq in vbr_downloads:
            if seq != "all":
                main(seq, save_dir)


    save_dir.mkdir(parents=True, exist_ok=True)

    ftp = ftplib.FTP(DATASET_LINK)
    ftp.login(FTP_USER, "")
    db_path = "vbr_slam/" + dataset.split("_")[0] + "/" + dataset
    ftp.cwd(db_path)
    try:
        available_files = ftp.nlst()
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            CONSOLE.log("[bold red] Invalid input sequence")
        else:
            raise

    CONSOLE.print(Panel(
        " ".join([f"{f}" for f in available_files]), title="Download table"))

    with Progress() as progress:
        for f in available_files:
            local_path = save_dir / "vbr_slam" / dataset.split("_")[0] / dataset
            local_path.mkdir(parents=True, exist_ok=True)
            local_fname = local_path / f
            fout = open(local_fname, "wb")
            task = progress.add_task(f"Downloading {f}", total=ftp.size(f))

            def write_cb(data):
                progress.update(task, advance=len(data))
                fout.write(data)

            ftp.retrbinary("RETR " + f, write_cb)
            fout.close()
    ftp.quit()
    CONSOLE.print("[bold green] Done!")


def entrypoint():
    tyro.cli(main)


if __name__ == "__main__":
    entrypoint()
