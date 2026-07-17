import glob
import importlib
import logging
import os
from typing import Dict, Set

import yaml

from .parsers import BaseParser


logger = logging.getLogger(__name__)


PARSERS = {
    ".pdf": "PDFParser",
    ".docx": "WordParser",
    ".doc": "WordParser",
    ".xlsx": "ExcelParser",
    ".xls": "ExcelParser",
    ".csv": "ExcelParser",
    ".txt": "DummyParser",
    ".jpg": "ImageParser",
    ".jpeg": "ImageParser",
    ".png": "ImageParser",
    ".msg": "MsgParser",
    ".pptx": "PPTParser",
    ".ppt": "PPTParser",
}


EXTRACTORS = {
    ".zip": "ZIPExtractor",
    ".7z": "SevenZExtractor",
}


def parse(
        input_path: str,
        output_dir: str | None = None,
        extra_args_base_path: str = "/app/cfgs/cfg.yaml",
        extra_args_overwrite: Dict | None = None
    ) -> BaseParser:
    """
    extra_args_base_path:
        path to cfg containing extra init args for each parser class globally,
        let user use this function without additional setting
    extra_args_overwrite:
        if need adjust in special case, can pass a dict to overwrite the above
        often used in tests only.
    """
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in PARSERS:
        raise ValueError(f"Unsupported file type: {ext}")
    else:
        module = importlib.import_module(".parsers", package=__package__)
        parser_cls = getattr(module, PARSERS[ext])
        extra_args = {}
        with open(extra_args_base_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)['extra_init_args']
            extra_args = cfg.get(parser_cls.__name__, {})
        extra_args |= extra_args_overwrite or {}
        parser = parser_cls(input_path, output_dir, **extra_args)
        return parser


def recursive_parse(input_path: str, output_dir: str, visited_set: Set = None, **parse_kwargs) -> None:
    if visited_set is None:
        visited_set = set()
    elif os.path.basename(input_path) in visited_set:
        return
    visited_set.add(os.path.basename(input_path))
    
    extension = os.path.splitext(input_path)[1].lower()
    os.makedirs(output_dir, exist_ok=True)

    if not extension:  # folder recursion
        for sub_input_path in glob.glob(f"{input_path}/*"):
            recursive_parse(sub_input_path, output_dir, visited_set, **parse_kwargs)

    elif extension in EXTRACTORS:  # compressed file recursion
        module = importlib.import_module(".extractors", package=__package__)
        extractor_cls = getattr(module, EXTRACTORS[extension], None)
        try:
            extractor = extractor_cls(input_path, output_dir)
            extract_folder = extractor.run()
        except Exception as e:
            logger.error(f"Failed to parse extracted folder {extract_folder}: {e}")
            return
        for sub_input_path in glob.glob(f"{extract_folder}/*"):
            recursive_parse(sub_input_path, output_dir, visited_set, **parse_kwargs)
    else:
        try:
            parser = parse(input_path, output_dir, **parse_kwargs)
            parser.run()
        except Exception as e:
            logger.error(f"Failed to parse file {input_path}: {e}")
