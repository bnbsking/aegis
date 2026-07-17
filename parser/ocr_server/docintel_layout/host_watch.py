import glob
from pathlib import Path, PosixPath
import os
import random
import subprocess
import shutil
import time
import traceback


current_dir = Path(__file__).absolute().parent


def write_log(content: str, log_path: PosixPath = current_dir / "logs" / "host" / "log.txt"):
    print(content)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {content}\n")


def ocr(input_folder: str):
    try:
        process = subprocess.Popen(
            ["bash", f"{input_folder}/run_list.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            write_log(line.strip())  # 即時看到 shell script log
        process.wait()

        if process.returncode != 0:
            raise Exception(f"{input_folder}/run_list.sh failed with exit code {process.returncode}")

    except Exception as e:
        write_log(f"OCR process failed: {traceback.format_exc()}. e={e}")


def watch(
        in_case_folder: PosixPath = current_dir / "_cases" / "in_case",
        out_case_folder: PosixPath = current_dir / "_cases" / "out_case"
    ):
    write_log("start watch in_case folder")
    while 1:
        input_folders = glob.glob(str(in_case_folder / "*"))
        if not input_folders:
            time.sleep(5)
            continue

        input_folder = random.sample(input_folders, 1)[0]
        write_log(f"found input folder: {input_folder}")
        
        size1 = os.path.getsize(input_folder)
        time.sleep(1)
        size2 = os.path.getsize(input_folder)
        if size1 == size2:
            ocr(input_folder)
            shutil.move(input_folder, out_case_folder)
            write_log(f"moved input folder to out_case: {input_folder}")
            time.sleep(1)


if __name__ == "__main__":
    watch()
