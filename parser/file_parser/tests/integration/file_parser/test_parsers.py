import base64
import hashlib
import json
import os
import re
from typing import Dict, List

from file_parser.parsers import (
    PDFParser,
    WordParser,
    ExcelParser,
    DummyParser,
    ImageParser,
    MsgParser,
    PPTParser,
)


def _compare_txt(txt1: str, txt2: str):
    if os.path.exists(txt1):
        with open(txt1, "r", encoding="utf-8") as f:
            content1 = re.sub(r'\s+', ' ', f.read()).strip()
    else:
        content1 = re.sub(r'\s+', ' ', txt1).strip()
    if os.path.exists(txt2):
        with open(txt2, "r", encoding="utf-8") as f:
            content2 = re.sub(r'\s+', ' ', f.read()).strip()
    else:
        content2 = re.sub(r'\s+', ' ', txt2).strip()
    assert content1 == content2


def _compare_json(json1: str | Dict, json2: str | Dict):
    if isinstance(json1, str) and os.path.exists(json1):
        with open(json1, "r", encoding="utf-8") as f:
            content1 = json.load(f)
    else:
        content1 = json.loads(json1) if isinstance(json1, str) else json1
    if isinstance(json2, str) and os.path.exists(json2):
        with open(json2, "r", encoding="utf-8") as f:
            content2 = json.load(f)
    else:
        content2 = json.loads(json2) if isinstance(json2, str) else json2
    assert content1 == content2


def _compare_image(image1: Dict, image2: Dict):
    assert image1["filename"] == image2["filename"]
    assert image1["mimetype"] == image2["mimetype"]
    assert hashlib.sha256(base64.b64decode(image1["data"])).hexdigest() == image2["sha256"]


def _compare_json_image(out: Dict, expected: Dict):
    _compare_json(
        {k: v for k, v in out.items() if k != "images"},
        {k: v for k, v in expected.items() if k != "images"},
    )
    expected_by_name = {i["filename"]: i for i in expected["images"]}
    assert {i["filename"] for i in out["images"]} == set(expected_by_name)
    for img in out["images"]:
        _compare_image(img, expected_by_name[img["filename"]])


pdf_url = "http://172.24.37.129:8002/run_pdf_list"
img_url = "http://172.24.37.129:8002/run_img_list"


class TestPDFParser:
    text_based_pdf_path = (
        "/data/_example_data/pdf/animals.pdf",
        "/data/_example_data/_expected_output/animals.pdf.txt"
    )

    img_only_pdf_path = (
        "/data/_example_data/pdf/animals_img_only.pdf",
        "/data/_example_data/_expected_output/animals.pdf.txt"
    )

    def test_parse_pdf_text_mode_text_pdf(self):
        ipath, opath = self.text_based_pdf_path
        parser = PDFParser(ipath, None, 'text', pdf_url, img_url, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)
    
    def test_parse_pdf_text_mode_img_pdf(self):
        ipath, _ = self.img_only_pdf_path
        parser = PDFParser(ipath, None, 'text', pdf_url, img_url, to_str=True)
        out = parser.run()
        _compare_txt(out.strip(), "")

    def test_parse_pdf_hybrid_mode_text_pdf(self):
        ipath, opath = self.text_based_pdf_path
        parser = PDFParser(ipath, None, 'hybrid', pdf_url, img_url, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)
    
    def test_parse_pdf_hybrid_mode_img_pdf(self):
        ipath, opath = self.img_only_pdf_path
        parser = PDFParser(ipath, None, 'hybrid', pdf_url, img_url, to_str=True)
        out = parser.run()
        print(out)
        """
        Dogs are the best friend of humane
        «J
        123 dogs are running in the yard.<

        J

        [anima na wo =i

        ms lo le

        kt
        """


class TestWordParser:
    docx_path = (
        "/data/_example_data/word/animals.docx",
        "/data/_example_data/_expected_output/animals.pdf.txt"
    )

    doc_path = (
        "/data/_example_data/word/animals.doc",
        "/data/_example_data/_expected_output/animals.pdf.txt"
    )

    def test_parse_docx(self):
        ipath, opath = self.docx_path
        parser = WordParser(ipath, None, 'hybrid', pdf_url, img_url, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)


    def test_parse_doc(self):
        ipath, opath = self.doc_path
        parser = WordParser(ipath, None, 'hybrid', pdf_url, img_url, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)


class TestExcelParser:
    csv_path = (
        "/data/_example_data/excel/dogs.csv",
        "/data/_example_data/_expected_output/dogs.csv.txt"
    )

    csv_path_json = (
        "/data/_example_data/excel/dogs.csv",
        "/data/_example_data/_expected_output/dogs.csv.json"
    )

    xlsx_path = (
        "/data/_example_data/excel/dogs_cats.xlsx",
        "/data/_example_data/_expected_output/dogs_cats.xlsx.txt"
    )

    xlsx_path_json = (
        "/data/_example_data/excel/dogs_cats.xlsx",
        "/data/_example_data/_expected_output/dogs_cats.xlsx.json"
    )

    xls_path = (
        "/data/_example_data/excel/dogs_cats.xls",
        "/data/_example_data/_expected_output/dogs_cats.xlsx.txt"
    )

    xls_path_json = (
        "/data/_example_data/excel/dogs_cats.xls",
        "/data/_example_data/_expected_output/dogs_cats.xlsx.json"
    )

    def test_parse_csv(self):
        ipath, opath = self.csv_path
        parser = ExcelParser(ipath, None, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)

    def test_parse_csv_json(self):
        ipath, opath = self.csv_path_json
        parser = ExcelParser(ipath, None, to_str=False)
        out = parser.run()
        _compare_json(out, opath)

    def test_parse_xlsx(self):
        ipath, opath = self.xlsx_path
        parser = ExcelParser(ipath, None, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)

    def test_parse_xlsx_json(self):
        ipath, opath = self.xlsx_path_json
        parser = ExcelParser(ipath, None, to_str=False)
        out = parser.run()
        _compare_json(out, opath)

    def test_parse_xls(self):
        ipath, opath = self.xls_path
        parser = ExcelParser(ipath, None, to_str=True)
        out = parser.run()
        _compare_txt(out, opath)

    def test_parse_xls_json(self):
        ipath, opath = self.xls_path_json
        parser = ExcelParser(ipath, None, to_str=False)
        out = parser.run()
        _compare_json(out, opath)


class TestDummyParser:
    txt_path = (
        "/data/_example_data/text/animals.txt",
        "/data/_example_data/_expected_output/animals.pdf.txt"
    )

    def test_parse_txt(self):
        ipath, opath = self.txt_path
        parser = DummyParser(ipath, None)
        out = parser.run()
        _compare_txt(out, opath)


class TestImageParser:
    jpg_path = ("/data/_example_data/img/animals.jpg", "")
    png_path = ("/data/_example_data/img/animals.png", "")

    def test_parse_jpg(self):
        ipath, _ = self.jpg_path
        parser = ImageParser(ipath, None, img_url)
        out = parser.run()
        print(out)
        #['Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n']
        
    def test_parse_png(self):
        ipath, _ = self.png_path
        parser = ImageParser(ipath, None, img_url)
        out = parser.run()
        print(out)
        #['Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n']


class TestMsgParser:
    msg_path = (
        "/data/_example_data/msg/health_tips.msg",
        "/data/_example_data/_expected_output/health_tips.msg.json",
    )

    def _compare_msg(self, out: Dict, expected_path: str):
        with open(expected_path, "r", encoding="utf-8") as f:
            expected = json.load(f)
        _compare_json_image(out, expected)

    def test_parse_msg(self):
        ipath, opath = self.msg_path
        parser = MsgParser(ipath, None)
        out = parser.run()
        self._compare_msg(out, opath)


class TestPPTParser:
    pptx_path = (
        "/data/_example_data/ppt/root_cause.pptx",
        "/data/_example_data/_expected_output/root_cause.pptx.json",
    )

    ppt_path = (
        "/data/_example_data/ppt/root_cause.ppt",
        "/data/_example_data/_expected_output/root_cause.pptx.json",
    )

    def _compare_ppt(self, out: List[Dict], expected_path: str):
        with open(expected_path, "r", encoding="utf-8") as f:
            expected = json.load(f)
        assert len(out) == len(expected)
        for slide, exp_slide in zip(out, expected):
            _compare_json_image(slide, exp_slide)

    def test_parse_pptx(self):
        ipath, opath = self.pptx_path
        parser = PPTParser(ipath, None)
        out = parser.run()
        self._compare_ppt(out, opath)

    def test_parse_ppt(self):
        ipath, opath = self.ppt_path
        parser = PPTParser(ipath, None)
        out = parser.run()
        self._compare_ppt(out, opath)


if __name__ == "__main__":
    # obj = TestPDFParser()
    # obj.test_parse_pdf_text_mode_text_pdf()
    # obj.test_parse_pdf_text_mode_img_pdf()
    # obj.test_parse_pdf_hybrid_mode_text_pdf()
    # obj.test_parse_pdf_hybrid_mode_img_pdf()
    
    # obj = TestWordParser()
    # obj.test_parse_docx()
    # obj.test_parse_doc()
    
    # obj = TestExcelParser()
    # obj.test_parse_csv()
    # obj.test_parse_csv_json()
    # obj.test_parse_xlsx()
    # obj.test_parse_xlsx_json()
    # obj.test_parse_xls()
    # obj.test_parse_xls_json()

    # obj = TestDummyParser()
    # obj.test_parse_txt()

    # obj = TestImageParser()
    # obj.test_parse_jpg()
    # obj.test_parse_png()

    obj = TestMsgParser()
    obj.test_parse_msg()

    obj = TestPPTParser()
    obj.test_parse_pptx()
    obj.test_parse_ppt()

    print("All passed")
