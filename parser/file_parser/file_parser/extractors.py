import os
import subprocess


class BaseExtractor:
    def __init__(self, input_path: str, output_dir: str = "/app/.tmp/_extract"):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)


class ZIPExtractor(BaseExtractor):
    def run(self) -> str:
        subprocess.run(f'unzip -o "{self.input_path}" -d "{self.output_dir}"', shell=True, check=True)
        return self.output_dir


class SevenZExtractor(BaseExtractor):
    def run(self) -> str:
        subprocess.run(f'7z x "{self.input_path}" -o"{self.output_dir}"', shell=True, check=True)
        return self.output_dir
