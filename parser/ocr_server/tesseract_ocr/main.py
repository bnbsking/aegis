from typing import List

import numpy as np
import pytesseract


class TesseractOCR:
    def run(self, img_list: List[np.ndarray]) -> List[str]:
        ocr_text_list = []
        for image_numpy in img_list:
            ocr_text = pytesseract.image_to_string(image_numpy, lang="eng+chi_sim+chi_tra")
            ocr_text_list.append(ocr_text)
        return ocr_text_list
