import requests


def test_easy_ocr():
    url = "http://localhost:8001/easy_ocr"
    files = {"file": open("/app/_data/receipt.pdf", "rb")}
    response = requests.post(url, files=files)
    print(response.text)


def test_easy_ocr2():
    url = "http://ocr:8001/easy_ocr"
    files = {"file": open("/app/_data/QC七大手法教育訓練課程-品保部-質量工具-李順順_5.pdf", "rb")}
    response = requests.post(url, files=files)
    print(response.text)


if __name__ == "__main__":
    test_easy_ocr()
    test_easy_ocr2()