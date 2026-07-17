import os
from tempfile import TemporaryDirectory

from file_parser.extractors import ZIPExtractor, SevenZExtractor


class TestZipExtractor:
    def test_run(self):
        input_path = "/data/_example_data/extractors/animals2.zip"
        filenames = ["animals2.jpg", "animals2.png"]
        
        with TemporaryDirectory() as output_dir:
            extractor = ZIPExtractor(input_path, output_dir)
            output_dir = extractor.run()
            for filename in filenames:
                assert os.path.exists(os.path.join(output_dir, filename))


class TestSevenZExtractor:
    def test_run(self):
        input_path = "/data/_example_data/extractors/animals.7z"
        filenames = ["animals.jpg", "animals.png"]
        
        with TemporaryDirectory() as output_dir:
            extractor = SevenZExtractor(input_path, output_dir)
            output_dir = extractor.run()
            for filename in filenames:
                assert os.path.exists(os.path.join(output_dir, filename))


if __name__ == "__main__":
    obj = TestZipExtractor()
    obj.test_run()

    obj = TestSevenZExtractor()
    obj.test_run()