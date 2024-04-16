from pathlib import Path
import ftplib
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from vbr_devkit.tools.console import console

DATASET_LINK = "151.100.59.119"
FTP_USER = "anonymous"

vbr_downloads = [
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

def download_seq_fld(seq: str, output_dir: Path) -> None:
    def human_readable_size(size, decimal_places=2):
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
            if size < 1024.0 or unit == 'PiB':
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"

    console.rule(f"[bold green] Downloading {seq}")
    # output_dir.mkdir(parents=True, exist_ok=True)

    # Establish FTP connection
    console.log(f"Connecting to {DATASET_LINK}")
    ftp = ftplib.FTP(DATASET_LINK)
    ftp.login(FTP_USER, "")
    console.log(":white_check_mark: Connection established")
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True) as progress:
        progress.add_task("Gathering files", total=None)
        db_path = "vbr_slam/" + seq.split("_")[0] + "/" + seq
        ftp.cwd(db_path)

        try:
            available_files = ftp.nlst()
            available_files = [(file, ftp.size(file)) for file in available_files]
        except ftplib.error_perm as resp:
            if str(resp) == "550 No files found":
                console.log("[bold red] Invalid input sequence")
            else:
                raise
        # Sort based on size
        available_files = sorted(available_files, key=lambda x: x[1])

    console.print(Panel(
        "\n".join(f"{f[0]}\t{human_readable_size(f[1])}" for f in available_files), title="Downloading files"
    ))

    available_files = [x[0] for x in available_files]
    # Downloading routine
    with Progress() as progress:
        for f in available_files:
            local_path = output_dir / "vbr_slam" / seq.split("_")[0] / seq
            local_path.mkdir(exist_ok=True, parents=True)
            local_fname = local_path / f
            fout = open(local_fname, "wb")
            task = progress.add_task(f"Downloading {f}", total=ftp.size(f))

            def write_cb(data):
                progress.update(task, advance=len(data))
                fout.write(data)

            ftp.retrbinary("RETR " + f, write_cb)
            fout.close()
    ftp.quit()
    console.print(":tada: Completed")
