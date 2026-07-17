import os
import requests


def test_run_pdf_list():
    pdf_path1 = "/data/_example_data/pdf/animals.pdf"
    pdf_path2 = "/data/_example_data/pdf/animals_img_only.pdf"
    url = "http://localhost:8001/run_pdf_list"

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
        ['STORE NAME l23 Sample Street, Country phone: 000|123-4567 RECEIPT Date: 2025-12-04 Receipt#: 00012345 Item Qty Unit Price Total USB Cable 2 $5.00 $10.00 Keyboard _ $25.00 $25.00 Wotebook 3 $2.50 $7.50 Subtotal: $42.50 Tax 5%|: $2.13 Total: $44.63 Thank you foryour purchase. City.'],
        ['are the bestfriend ofhumans 123 dogs are runningin the yard.- Animal~ Height- Weight- Dog- 100< 10~ Cate 50. 5 Dogs']
    ]
    """


def test_run_img_list():
    img_path1 = "/data/_example_data/img/animals.jpg"
    img_path2 = "/data/_example_data/img/animals.png"
    url = "http://localhost:8001/run_img_list"

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
        'Dogs are the bestfriend ofhuman 123 dogs are runningin the yard.- Animal Height- Weight- Dog 100 10 Cat 50',
        'Dogs are the bestfriend ofhuman 123 dogs are runningin the yard.- Animal Height Weight Dog 100 10 Cat 50'
    ]
    """


if __name__ == "__main__":
    test_run_pdf_list()
    test_run_img_list()
