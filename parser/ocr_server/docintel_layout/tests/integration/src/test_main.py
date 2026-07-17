from src.main import DocIntelLayout


class TestDocIntelLayout:
    def test_run_pdf_list(self):
        ocr = DocIntelLayout()

        pdf_bytes_list = []
        with open("/data/_example_data/pdf/animals.pdf", "rb") as f:
            pdf_bytes = f.read()
            pdf_bytes_list.append(pdf_bytes)
        with open("/data/_example_data/pdf/animals_img_only.pdf", "rb") as f:
            pdf_bytes = f.read()
            pdf_bytes_list.append(pdf_bytes)

        layout_list = ocr.run_pdf_list(pdf_bytes_list)
        print(layout_list)
        """
        """


if __name__ == "__main__":
    obj = TestDocIntelLayout()
    obj.test_run_pdf_list()
    