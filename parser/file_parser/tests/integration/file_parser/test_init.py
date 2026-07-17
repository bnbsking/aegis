import os
from tempfile import TemporaryDirectory

from file_parser import parse, recursive_parse
from file_parser.parsers import (
    PDFParser,
    WordParser,
    ExcelParser,
    ImageParser,
    DummyParser,
    MsgParser,
    PPTParser,
)


def test_parse_pdf():
    obj = parse("/data/_example_data/pdf/animals.pdf")
    assert isinstance(obj, PDFParser)
    out = obj.run()
    print(out)
    """
    ['Dogs are the best friend of human \n \n123 dogs are running in the yard. \n \nAnimal \nHeight \nWeight \nDog \n100 \n10 \nCat \n50 \n5 \n \n']
    """


def test_parse_pdf_to_str():
    obj = parse("/data/_example_data/pdf/animals.pdf", extra_args_overwrite={"to_str": True})
    assert isinstance(obj, PDFParser)
    out = obj.run()
    print(out)
    """
    Dogs are the best friend of human 
 
    123 dogs are running in the yard. 
    
    Animal 
    Height 
    Weight 
    Dog 
    100 
    10 
    Cat 
    50 
    5 
    """


def test_parse_pdf_img_only():
    obj = parse("/data/_example_data/pdf/animals_img_only.pdf")
    assert isinstance(obj, PDFParser)
    out = obj.run()
    print(out)
    """
    [' \nDogs are the best friend of humane\n\na\n\n123 dogs are running in the yard.\n\net\n\nma mao Two 天 天 國 點\n\n']
    """


def test_parse_pdf_img_only_to_str():
    obj = parse("/data/_example_data/pdf/animals_img_only.pdf", extra_args_overwrite={"to_str": True})
    assert isinstance(obj, PDFParser)
    out = obj.run()
    print(out)
    """
    Dogs are the best friend of humane

    a

    123 dogs are running in the yard.

    et

    ma mao Two 天 天 國 點
    """


def test_parse_word_docx():
    obj = parse("/data/_example_data/word/animals.docx")
    assert isinstance(obj, WordParser)
    out = obj.run()
    print(out)
    """
    ['Dogs are the best friend of human\n123 dogs are running in the yard.\nAnimal\nHeight\nWeight\nDog\n100\n10\nCat\n50\n5\n']
    """


def test_parse_word_docx_to_str():
    obj = parse("/data/_example_data/word/animals.docx", extra_args_overwrite={"to_str": True})
    assert isinstance(obj, WordParser)
    out = obj.run()
    print(out)
    """
    Dogs are the best friend of human
    123 dogs are running in the yard.
    Animal
    Height
    Weight
    Dog
    100
    10
    Cat
    50
    5
    """


def test_parse_word_doc():
    obj = parse("/data/_example_data/word/animals.doc")
    assert isinstance(obj, WordParser)
    out = obj.run()
    print(out)
    """
    ['Dogs are the best friend of human\n123 dogs are running in the yard.\nAnimal\nHeight\nWeight\nDog\n100\n10\nCat\n50\n5\n']
    """


def test_parse_word_doc_to_str():
    obj = parse("/data/_example_data/word/animals.doc", extra_args_overwrite={"to_str": True})
    assert isinstance(obj, WordParser)
    out = obj.run()
    print(out)
    """
    Dogs are the best friend of human
    123 dogs are running in the yard.
    Animal
    Height
    Weight
    Dog
    100
    10
    Cat
    50
    5
    """


def test_parse_excel_csv():
    obj = parse("/data/_example_data/excel/dogs.csv")
    assert isinstance(obj, ExcelParser)
    out = obj.run()
    print(out)
    """
    [{'dog_id': 1, 'name': 'Buddy', 'breed': 'Golden Retriever', 'age': 3, 'color': 'Golden', 'weight_kg': 30.5}, {'dog_id': 2, 'name': 'Luna', 'breed': 'Border Collie', 'age': 2, 'color': 'Black and White', 'weight_kg': 18.2}, {'dog_id': 3, 'name': 'Max', 'breed': 'German Shepherd', 'age': 5, 'color': 'Brown', 'weight_kg': 34.0}, {'dog_id': 4, 'name': 'Daisy', 'breed': 'Poodle', 'age': 4, 'color': 'White', 'weight_kg': 12.8}, {'dog_id': 5, 'name': 'Charlie', 'breed': 'Beagle', 'age': 1, 'color': 'Tri-color', 'weight_kg': 9.6}]
    """


def test_parse_excel_csv_to_str():
    obj = parse("/data/_example_data/excel/dogs.csv", extra_args_overwrite={"to_str": True})
    assert isinstance(obj, ExcelParser)
    out = obj.run()
    print(out)
    """
    dog_id    name            breed  age           color  weight_kg
    1   Buddy Golden Retriever    3          Golden       30.5
    2    Luna    Border Collie    2 Black and White       18.2
    3     Max  German Shepherd    5           Brown       34.0
    4   Daisy           Poodle    4           White       12.8
    5 Charlie           Beagle    1       Tri-color        9.6
    cat_id     name              breed  age       color  weight_kg
    1 Whiskers Domestic Shorthair    4        Gray        4.2
    2     Luna            Siamese    2       Cream        3.6
    3   Oliver  British Shorthair    5        Blue        5.8
    4     Milo         Maine Coon    3 Brown Tabby        6.9
    5    Bella            Persian    6       White        4.9
    """


def test_parse_excel_xlsx():
    obj = parse("/data/_example_data/excel/dogs_cats.xlsx")
    assert isinstance(obj, ExcelParser)
    out = obj.run()
    print(out)
    """
    [{'dog_id': 1, 'name': 'Buddy', 'breed': 'Golden Retriever', 'age': 3, 'color': 'Golden', 'weight_kg': 30.5}, {'dog_id': 2, 'name': 'Luna', 'breed': 'Border Collie', 'age': 2, 'color': 'Black and White', 'weight_kg': 18.2}, {'dog_id': 3, 'name': 'Max', 'breed': 'German Shepherd', 'age': 5, 'color': 'Brown', 'weight_kg': 34.0}, {'dog_id': 4, 'name': 'Daisy', 'breed': 'Poodle', 'age': 4, 'color': 'White', 'weight_kg': 12.8}, {'dog_id': 5, 'name': 'Charlie', 'breed': 'Beagle', 'age': 1, 'color': 'Tri-color', 'weight_kg': 9.6}]
    """


def test_parse_excel_xlsx_to_str():
    obj = parse("/data/_example_data/excel/dogs_cats.xlsx", extra_args_overwrite={"to_str": True})
    assert isinstance(obj, ExcelParser)
    out = obj.run()
    print(out)
    """
    dog_id    name            breed  age           color  weight_kg
    1   Buddy Golden Retriever    3          Golden       30.5
    2    Luna    Border Collie    2 Black and White       18.2
    3     Max  German Shepherd    5           Brown       34.0
    4   Daisy           Poodle    4           White       12.8
    5 Charlie           Beagle    1       Tri-color        9.6
    cat_id     name              breed  age       color  weight_kg
      1 Whiskers Domestic Shorthair    4        Gray        4.2
      2     Luna            Siamese    2       Cream        3.6
      3   Oliver  British Shorthair    5        Blue        5.8
      4     Milo         Maine Coon    3 Brown Tabby        6.9
      5    Bella            Persian    6       White        4.9
    """


def test_parse_jpg():
    obj = parse("/data/_example_data/img/animals.jpg")
    assert isinstance(obj, ImageParser)
    out = obj.run()
    print(out)
    # ['Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n']


def test_parse_png():
    obj = parse("/data/_example_data/img/animals.png")
    assert isinstance(obj, ImageParser)
    out = obj.run()
    print(out)
    # ['Dogs are the best friend of humane’\n\n123 dogs are running in the yard.«\n\nAnimal Heighte Weighte\nDoge 100¢ 106\nCate 502 5e\n\n']


def test_parse_txt():
    obj = parse("/data/_example_data/text/animals.txt")
    assert isinstance(obj, DummyParser)
    out = obj.run()
    print(out)
    """
    Dogs are the best friend of human

    123 dogs are running in the yard.

    Animal
    Height
    Weight
    Dog
    100
    10
    Cat
    50
    5
    """


def test_parse_msg():
    obj = parse("/data/_example_data/msg/health_tips.msg")
    assert isinstance(obj, MsgParser)
    out = obj.run()
    print(out["subject"])
    """
    【健康宣導】7月 改善脂肪肝五原則
    """


def test_parse_pptx():
    obj = parse("/data/_example_data/ppt/root_cause.pptx")
    assert isinstance(obj, PPTParser)
    out = obj.run()
    print(out[0]["text"])
    """
    異常確認-summary
    """


def test_parse_ppt():
    obj = parse("/data/_example_data/ppt/root_cause.ppt")
    assert isinstance(obj, PPTParser)
    out = obj.run()
    print(out[0]["text"])
    """
    異常確認-summary
    """


def test_recursive_parse():
    filenames = ["animals.jpg", "animals.png", "animals2.jpg", "animals2.png"]\
        + ["animals.json", "animals2.json"]

    with TemporaryDirectory() as temp_dir:
        recursive_parse("/data/_example_data/extractors", temp_dir)
        for filename in filenames:
            assert os.path.exists(os.path.join(temp_dir, filename))
            if filename.endswith(".json") or filename.endswith(".txt"):
                with open(os.path.join(temp_dir, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"Content of {filename}:")
                    print(content)
    """
    Content of animals.json:
    [
        "Dogs are the best friend of humane’\n\n123 dogs are running in the yard.\n\nAnimate Heighte Weighte\nDoge 1008 108\nCate 502 5e\n\n"
    ]
    Content of animals2.json:
    [
        "Dogs are the best friend of humane’\n\n123 dogs are running in the yard.\n\nAnimate Heighte Weighte\nDoge 1008 108\nCate 502 5e\n\n"
    ]
    """


if __name__ == "__main__":
    # test_parse_pdf()
    # test_parse_pdf_to_str()
    # test_parse_pdf_img_only()
    # test_parse_pdf_img_only_to_str()

    # test_parse_word_docx()
    # test_parse_word_docx_to_str()
    # test_parse_word_doc()
    # test_parse_word_doc_to_str()

    # test_parse_excel_csv()
    # test_parse_excel_csv_to_str()
    # test_parse_excel_xlsx()
    # test_parse_excel_xlsx_to_str()

    # test_parse_jpg()
    # test_parse_png()

    #test_parse_txt()

    test_parse_msg()

    test_parse_pptx()
    test_parse_ppt()

    test_recursive_parse()

    print("All passed")
