from tesseract_ocr.main import TesseractOCR


class TestTesseractOCR:
    def test_run_pdf_list(self):
        ocr = TesseractOCR()

        pdf_bytes_list = []
        with open("/data/_example_data/pdf/text_based.pdf", "rb") as f:
            pdf_bytes = f.read()
            pdf_bytes_list.append(pdf_bytes)
        with open("/data/_example_data/pdf/img_only.pdf", "rb") as f:
            pdf_bytes = f.read()
            pdf_bytes_list.append(pdf_bytes)

        text_list = ocr.run_pdf_list(pdf_bytes_list)
        print(text_list)
        """
        [
            ['STORE NAME\n\n123 Sample Street, City, Country\nPhone: (000) 123-4567\n\nRECEIPT\n\nDate: 2025-12-04\nReceipt #: 00012345\n\nItem Unit Price\n\nUSB Cable $5.00\nKeyboard $25.00\nNotebook $2.50\n\nSubtotal: $42.50\nTax (5%): $2.13\n\nTotal: $44.63\n\nThank you for your purchase!\n'],
            ['Dogs are the best friend of humane\n關\n\n123 dogs are running in the yard.<\n\neI\n\nam ma wa 還 還 點\n-\n\n']
        ]
        """
    
    def test_run_img_list(self):
        ocr = TesseractOCR()

        image_bytes_list = []
        with open("/data/_example_data/img/img_only.jpg", "rb") as f:
            image_bytes = f.read()
            image_bytes_list.append(image_bytes)
        with open("/data/_example_data/img/img_only.png", "rb") as f:
            image_bytes = f.read()
            image_bytes_list.append(image_bytes)

        text_list = ocr.run_img_list(image_bytes_list)
        print(text_list)
        """
        [
            'Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n',
            'Dogs are the best friend of humane’\n\n123 dogs are running in the yard.\n\nAnimate Heighte Weighte\nDoge 1008 108\nCate 502 5e\n\n'
        ]
        """


if __name__ == "__main__":
    obj = TestTesseractOCR()
    obj.test_run_pdf_list()
    obj.test_run_img_list()
    