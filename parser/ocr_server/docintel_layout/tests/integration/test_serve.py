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
    [
    {'json': {'document_info': {'filename': 'temp', 'source_path': '/data/input/temp.pdf', 'processed_at': '2026-07-20T00:45:36.637378', 'model_id': 'prebuilt-layout', 'content_format': 'DocumentContentFormat.MARKDOWN'}, 'extraction_summary': {'figures': 0, 'handwritten_regions': 0, 'key_value_pairs': 0, 'tables': 1}, 'figures': [], 'handwritten_regions': [], 'key_value_pairs': {}, 'tables': [{'columns': ['Animal', 'Dog', 'Cat'], 'rows': [{'Animal': 'Height / Weight', 'Dog': '100 / 10', 'Cat': '50 / 5'}], 'classification': 'vertical', 'table_index': 1, 'metadata': {'row_count': 3, 'column_count': 3, 'page_number': 1}}], 'pages': 1}, 'markdown': 'Dogs are the best friend of human\n\n123 dogs are running in the yard.\n\n\n<table>\n<tr>\n<th>Animal</th>\n<th>Height</th>\n<th>Weight</th>\n</tr>\n<tr>\n<td>Dog</td>\n<td>100</td>\n<td>10</td>\n</tr>\n<tr>\n<td>Cat</td>\n<td>50</td>\n<td>5</td>\n</tr>\n</table>\n'},
    {'json': {'document_info': {'filename': 'temp', 'source_path': '/data/input/temp.pdf', 'processed_at': '2026-07-20T00:45:50.393199', 'model_id': 'prebuilt-layout', 'content_format': 'DocumentContentFormat.MARKDOWN'}, 'extraction_summary': {'figures': 0, 'handwritten_regions': 1, 'key_value_pairs': 0, 'tables': 1}, 'figures': [], 'handwritten_regions': [{'index': 1, 'page_number': 1, 'image_file': 'temp_handwritten_1_1.png', 'image_url': 'temp_handwritten_1_1.png', 'bounding_box': {'min_x': 1.3698, 'min_y': 3.5169, 'max_x': 1.4768, 'max_y': 3.6435}, 'word_count': 1, 'text_content': '1'}], 'key_value_pairs': {}, 'tables': [{'columns': ['Animal', 'Dog', 'Cat-'], 'rows': [{'Animal': 'unselected: / Height :unselected: / Weight+', 'Dog': '100¢ :unselected: / 10+ :unselected:', 'Cat-': '50€ :unselected: / 5€'}], 'classification': 'vertical', 'table_index': 1, 'metadata': {'row_count': 3, 'column_count': 3, 'page_number': 1}}], 'pages': 1}, 'markdown': 'Dogs are the best friend of human‹\n\n€\n\n123 dogs are running in the yard.«\n\n4\n\n\n<table>\n<tr>\n<th>Animal ☐</th>\n<th>Height ☐</th>\n<th>Weight+</th>\n</tr>\n<tr>\n<td>Dog</td>\n<td>100¢ ☐</td>\n<td>10+ ☐</td>\n</tr>\n<tr>\n<td>Cat-</td>\n<td>50€ ☐</td>\n<td>5€</td>\n</tr>\n</table>\n\n\n€\n\n€\n\n€\n\n1\n'}
    ]
    """


if __name__ == "__main__":
    test_run_pdf_list()
    