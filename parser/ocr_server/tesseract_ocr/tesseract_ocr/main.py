from tempfile import TemporaryDirectory
from typing import List

import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import pytesseract


class TesseractOCR:
    def _run_pdf(self, pdf_bytes: bytes) -> List[str]:
        with TemporaryDirectory() as tmp_dir:
            pdf_path = f"{tmp_dir}/temp.pdf"
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            img_list = convert_from_path(pdf_path, dpi=300)
        
        ocr_text_list = []
        for img in img_list:
            ocr_text = pytesseract.image_to_string(np.array(img), lang="eng+chi_sim+chi_tra")
            ocr_text_list.append(ocr_text)
        return ocr_text_list
    
    def run_pdf_list(self, pdf_bytes_list: List[bytes]) -> List[List[str]]:
        return [self._run_pdf(pdf_bytes) for pdf_bytes in pdf_bytes_list]

    def _run_img(self, image_bytes: bytes) -> str:
        with TemporaryDirectory() as tmp_dir:
            image_path = f"{tmp_dir}/temp.jpg"
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            img = Image.open(image_path)

        ocr_text = pytesseract.image_to_string(np.array(img), lang="eng+chi_sim+chi_tra")
        return ocr_text
    
    def run_img_list(self, image_bytes_list: List[bytes]) -> List[str]:
        return [self._run_img(image_bytes) for image_bytes in image_bytes_list]
