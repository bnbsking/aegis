import os
import requests


def test_run_pdf_list():
    pdf_path1 = "/data/_example_data/pdf/text_based.pdf"
    pdf_path2 = "/data/_example_data/pdf/img_only.pdf"
    url = "http://localhost:8002/run_pdf_list"

    files = [
        ("files", open(pdf_path1, "rb")),
        ("files", open(pdf_path2, "rb"))
    ]
    data = {"extra_msg": "none"}
    response = requests.post(url, files=files, data=data)

    out = response.json()
    print(out)
    """
    [
     ['STORE NAME\n\n123 Sample Street, City, Country\nPhone: (000) 123-4567\n\nRECEIPT\n\nDate: 2025-12-04\nReceipt #: 00012345\n\nItem Unit Price\n\nUSB Cable $5.00\nKeyboard $25.00\nNotebook $2.50\n\nSubtotal: $42.50\nTax (5%): $2.13\n\nTotal: $44.63\n\nThank you for your purchase!\n'],
     ['Dogs are the best friend of humane\n關\n\n123 dogs are running in the yard.<\n\neI\n\nam ma wa 還 還 點\n-\n\n']
    ]   
    """


def test_run_img_list():
    img_path1 = "/data/_example_data/img/img_only.jpg"
    img_path2 = "/data/_example_data/img/img_only.png"
    url = "http://localhost:8002/run_img_list"

    files = [
        ("files", open(img_path1, "rb")),
        ("files", open(img_path2, "rb"))
    ]
    data = {"extra_msg": "none"}
    response = requests.post(url, files=files, data=data)

    out = response.json()
    print(out)
    """
    [
     'Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n',
     'Dogs are the best friend of humane’\n\n123 dogs are running in the yard.\n\nAnimate Heighte Weighte\nDoge 1008 108\nCate 502 5e\n\n'
    ]
    """


if __name__ == "__main__":
    test_run_pdf_list()
    test_run_img_list()
