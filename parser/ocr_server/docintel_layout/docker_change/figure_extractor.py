"""Extract and save figures from PDF documents."""
import io
import re
import logging
import fitz
from PIL import Image
from config import Config


class FigureExtractor:
    """Extract figures/images from analyzed documents."""
    
    def __init__(self, storage_manager):
        """Initialize figure extractor.
        
        Args:
            storage_manager: StorageManager instance for saving images
        """
        self.storage_manager = storage_manager
    
    def extract_figures(self, result, pdf_document, filename, output_folder=None):
        """Extract figures from document analysis results.
        
        Args:
            result: AnalyzeResult from Document Intelligence
            pdf_document: PyMuPDF document object
            filename: Base filename for extracted images
            output_folder: Local output folder (optional)
            
        Returns:
            tuple: (modified_content, figure_count) - Content with figure URLs and count
        """
        if not result.figures:
            logging.debug("No figures found.")
            return result.content, 0
        
        logging.info(f"Extracting {len(result.figures)} figures...")
        
        image_urls = []
        figure_numbers = []
        
        for figure in result.figures:
            # Extract figure region from PDF
            if figure.bounding_regions:
                region = figure.bounding_regions[0]
                page = pdf_document.load_page(region.page_number - 1)
                polygon = region.polygon
                
                # Scale coordinates from inches to points
                scaled_polygon = [coord * Config.COORDINATE_SCALING_FACTOR for coord in polygon]
                if 0:
                    rect = fitz.Rect(scaled_polygon[0], scaled_polygon[1], scaled_polygon[4], scaled_polygon[5])
                    pix = page.get_pixmap(clip=rect, dpi=Config.IMAGE_DPI)
                else:
                    # 修正 1: 確保 Rect 坐標是有效的 (x0, y0, x1, y1)
                    # 有時候 polygon 的順序會導致 rect 寬高為負
                    x_coords = scaled_polygon[0::2]
                    y_coords = scaled_polygon[1::2]
                    rect = fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords))
                    
                    # 修正 2: 處理邊界溢出（長表格常見問題）
                    # 如果 rect 區域非常大，搭配高 DPI 會導致記憶體崩潰
                    pix = page.get_pixmap(clip=rect, dpi=Config.IMAGE_DPI, alpha=False)
            else:
                page = pdf_document.load_page(figure.page_number - 1)
                pix = page.get_pixmap(dpi=Config.IMAGE_DPI)
            
            figure_numbers.append(figure.id)
            
            # Convert to PNG bytes
            if 0:
                img = Image.open(io.BytesIO(pix.tobytes()))
            else:
                img_samples = pix.tobytes("ppm") 
                img = Image.open(io.BytesIO(img_samples))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()
            
            # Save image
            image_name = f"{filename}_figure_{figure.id}_highres.png"
            url = self.storage_manager.save_image(img_data, image_name, output_folder)
            
            if url:
                image_urls.append(url)
            
            img.close()
        
        # Insert image URLs into markdown content
        content = result.content
        for index, url in enumerate(image_urls):
            content = content.replace(
                "<figure>",
                f"<figure{index + 1}>\n![image_{figure_numbers[index]}]({url})\n",
                1
            )
        
        # Clean up figure tags
        content = re.sub(r"<figure\d+>", "<figure>", content)
        
        logging.info(f"Extracted {len(result.figures)} figures")
        return content, len(result.figures)
