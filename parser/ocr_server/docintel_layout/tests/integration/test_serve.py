import os
import requests


def test_run_pdf_list():
    pdf_path1 = "/data/_example_data/pdf/animals.pdf"
    pdf_path2 = "/data/_example_data/pdf/animals_img_only.pdf"
    url = "http://localhost:8003/run_pdf_list"

    files = [
        ("files", open(pdf_path1, "rb")),
        ("files", open(pdf_path2, "rb"))
    ]
    data = {"extra_msg": "none"}
    response = requests.post(url, files=files, data=data)

    out = response.json()
    print(out)
    """
    """


if __name__ == "__main__":
    test_run_pdf_list()
    