import requests

from file_parser.ocr_client import request_ocr


def test_request_ocr_pdf():
    pdf_path1 = "/data/_example_data/pdf/animals.pdf"
    pdf_path2 = "/data/_example_data/pdf/animals_img_only.pdf"
    url = "http://172.24.37.129:8002/run_pdf_list"

    with open(pdf_path1, "rb") as f1, open(pdf_path2, "rb") as f2:
        pdf_bytes_list = [f1.read(), f2.read()]
    out = request_ocr(pdf_bytes_list, url)
    print(out)
    """
    [
        ['Dogs are the best friend of human\n\n123 dogs are running in the yard.\n\nAnimal Height Weight\nDog 100 10\nCat 50 5\n\n'],
        ['圖 =\n\nDogs are the best friend of humane\n\na\n\n123 dogs are running in the yard.\n\n«J\n\n']
    ]
    """


def test_request_ocr_img():
    img_path1 = "/data/_example_data/img/animals.jpg"
    img_path2 = "/data/_example_data/img/animals.png"
    url = "http://172.24.37.129:8002/run_img_list"

    with open(img_path1, "rb") as f1, open(img_path2, "rb") as f2:
        img_bytes_list = [f1.read(), f2.read()]
    out = request_ocr(img_bytes_list, url)
    print(out)
    """
    [
        'Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n',
        'Dogs are the best friend of humane’\n\n123 dogs are running in the yard.\n\nAnimate Heighte Weighte\nDoge 1008 108\nCate 502 5e\n\n'
    ]
    """


if __name__ == "__main__":
    test_request_ocr_pdf()
    test_request_ocr_img()
