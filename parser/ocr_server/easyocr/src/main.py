from tempfile import TemporaryDirectory
from typing import List

import easyocr
import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image


class EasyOCR:
    def __init__(
            self,
            lang_list: List[str] = ['ch_tra', 'en'],  # ch_sim cannot used with ch_tra
            model_storage_directory: str = "/model/_easyocr",
        ):
        self.reader = easyocr.Reader(
            lang_list,
            model_storage_directory=model_storage_directory,
        )

    def _run_pdf(self, pdf_bytes: bytes) -> List[str]:
        pages = convert_from_bytes(pdf_bytes, dpi=300)
        out = []
        for i, page in enumerate(pages):
            #print(f"--- Page {i+1} ---")
            img_np = np.array(page)
            result = self.reader.readtext(img_np)
            page_blocks = []
            for (bbox, text, prob) in result:
                #print(f"{text} (confidence: {prob:.2f})")
                page_blocks.append(text)
            out.append(" ".join(page_blocks))
        return out
    
    def run_pdf_list(self, pdf_bytes_list: List[bytes]) -> List[List[str]]:
        return [self._run_pdf(pdf_bytes) for pdf_bytes in pdf_bytes_list]

    def _run_img(self, image_bytes: bytes) -> str:
        with TemporaryDirectory() as tmp_dir:
            image_path = f"{tmp_dir}/temp.jpg"
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            img = Image.open(image_path)

        img_np = np.array(img)
        result = self.reader.readtext(img_np)
        text_blocks = [text for (bbox, text, prob) in result]
        return " ".join(text_blocks)

    def run_img_list(self, image_bytes_list: List[bytes]) -> List[str]:
        return [self._run_img(image_bytes) for image_bytes in image_bytes_list]
