import argparse
import glob
from typing import Dict

import yaml

from deid.main import DeidPipeline


class TestDeidPipeline:
    def __init__(self, pipeline_args: Dict, pipeline_args_test: Dict):
        self.pipeline = DeidPipeline(**pipeline_args)
        txt_glob_path = f"{pipeline_args_test['txt_folder']}/*.txt"
        self.txt_path_list = sorted(glob.glob(txt_glob_path))
        assert len(self.txt_path_list) > 0, f"No txt found in {txt_glob_path}."

    def test_run_multiple(self):
        pass_list = []
        for txt_path in self.txt_path_list:
            print(f"========== txt_path: {txt_path} ==========")
            with open(txt_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            out = self.pipeline.run(raw_text)
            pass_list.append(not out.startswith("[Deid_failed]"))
        assert all(pass_list), f"Some deid failed. pass_list: {pass_list}"
        print("All passed :D")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exp_folder",
        "-e",
        type=str, 
        default="/app/exps/main/example"
    )
    args = parser.parse_args()
    cfg = yaml.safe_load(open(f"{args.exp_folder}/cfg.yaml", "r", encoding="utf-8"))
    test_obj = TestDeidPipeline(
        cfg["pipeline_args"],
        cfg["pipeline_args_test"]
    )
    test_obj.test_run_multiple()
