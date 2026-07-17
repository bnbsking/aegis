from datetime import datetime
import glob
import logging
import json
import os
import time
import shutil
from typing import Dict, List
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)


class DocIntelLayout:
    def __init__(self):
        pass

    def _run_pdf(self, pdf_bytes: bytes) -> Dict:
        timez = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y%m%d_%H%M%S")

        # put
        in_case_folder = f"/app/_cases/in_case/{timez}"
        shutil.copytree("/app/_template", in_case_folder, dirs_exist_ok=True)
        pdf_path = f"{in_case_folder}/input/temp.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        
        # polling
        out_case_folder = f"/app/_cases/out_case/{timez}"
        while not os.path.exists(out_case_folder):
            time.sleep(5)

        # output
        out = {"json": {}, "markdown": ""}
        for json_file in glob.glob(f"{out_case_folder}/output/*/*_analysis_result.json"):
            with open(json_file, "r") as f:
                out["json"] = json.load(f)
            
        for md_file in glob.glob(f"{out_case_folder}/output/*/*_layout.md"):
            with open(md_file, "r") as f:
                out["markdown"] = f.read()
        return out

    def run_pdf_list(self, pdf_bytes_list: List[bytes]) -> List[Dict]:
        return [self._run_pdf(pdf_bytes) for pdf_bytes in pdf_bytes_list]
