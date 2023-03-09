import os
import time
import shutil
from pathlib import Path
from typing import List, Tuple


def check_file_size(path: Path, timeout: float = 10.0):
    """Check file size every second

    Args:
        path (Path): _description_
        timeout (float, optional): timeout to break loop. Defaults to 10.0.
    """
    size = os.path.getsize(path)

    tic = time.time()
    # wait until the file size stops changing
    while True:
        time.sleep(1)  # wait 1 second before checking again
        new_size = os.path.getsize(path)

        if time.time() - tic > timeout:
            return False

        if new_size == size:
            break
        size = new_size

    return True


def get_files(
    path: Path, sort_by_modification_date: bool = False
) -> Tuple[List[Path], int]:
    files = [
        Path(os.path.join(path, f))
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
    ]

    if sort_by_modification_date:
        files.sort(
            key=lambda x: os.path.getmtime(os.path.join(path, x)),
        )

    return files, len(files)


def move(src: str, dest: str):
    shutil.move(
        src=src,
        dst=dest,
    )
