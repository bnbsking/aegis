from tesseract_ocr.main import TesseractOCR


class TestTesseractOCR:
    def test_run_pdf_list(self):
        ocr = TesseractOCR()

        pdf_bytes_list = []
        with open("/data/_example_data/pdf/animals.pdf", "rb") as f:
            pdf_bytes = f.read()
            pdf_bytes_list.append(pdf_bytes)
        with open("/data/_example_data/pdf/animals_img_only.pdf", "rb") as f:
            pdf_bytes = f.read()
            pdf_bytes_list.append(pdf_bytes)

        text_list = ocr.run_pdf_list(pdf_bytes_list)
        print(text_list)
        """
        [
            ['Dogs are the best friend of human\n\n123 dogs are running in the yard.\n\nAnimal Height Weight\nDog 100 10\nCat 50 5\n\n'],
            ['圖 =\n\nDogs are the best friend of humane\n\na\n\n123 dogs are running in the yard.\n\n«J\n\n']
        ]
        """
    
    def test_run_img_list(self):
        ocr = TesseractOCR()

        image_bytes_list = []
        with open("/data/_example_data/img/animals.jpg", "rb") as f:
            image_bytes = f.read()
            image_bytes_list.append(image_bytes)
        with open("/data/_example_data/img/animals.png", "rb") as f:
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
    