from pypdf import PdfReader, PdfWriter

def extract_first_five_pages(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Determine how many pages to extract (handle PDFs with <5 pages)
    num_pages = min(5, len(reader.pages))

    for page_num in range(num_pages):
        writer.add_page(reader.pages[page_num])

    # Save the new PDF
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Successfully extracted {num_pages} pages to '{output_pdf_path}'")

# Example usage
input_pdf = "./_data/QC七大手法教育訓練課程-品保部-質量工具-李順順.pdf"
output_pdf = "./_data/QC七大手法教育訓練課程-品保部-質量工具-李順順_5.pdf"

extract_first_five_pages(input_pdf, output_pdf)