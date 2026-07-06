from src.main import EasyOCR


class TestEasyOCR:
    def test_run_pdf_list(self):
        ocr = EasyOCR()

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
            ['STORE NAME l23 Sample Street, Country phone: 000|123-4567 RECEIPT Date: 2025-12-04 Receipt#: 00012345 Item Qty Unit Price Total USB Cable 2 $5.00 $10.00 Keyboard _ $25.00 $25.00 Wotebook 3 $2.50 $7.50 Subtotal: $42.50 Tax 5%|: $2.13 Total: $44.63 Thank you foryour purchase. City.'],
            ['are the bestfriend ofhumans 123 dogs are runningin the yard.- Animal~ Height- Weight- Dog- 100< 10~ Cate 50. 5 Dogs']
        ]
        """
    
    def test_run_img_list(self):
        ocr = EasyOCR()

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
            'Dogs are the bestfriend ofhuman 123 dogs are runningin the yard.- Animal Height- Weight- Dog 100 10 Cat 50',
            'Dogs are the bestfriend ofhuman 123 dogs are runningin the yard.- Animal Height Weight Dog 100 10 Cat 50'
        ]
        """


if __name__ == "__main__":
    obj = TestEasyOCR()
    #obj.test_run_pdf_list()
    obj.test_run_img_list()
    