"""Storage management for local storage."""

import io
import logging
import os
from typing import Optional


class StorageManager:
    """Handle file storage operations for local storage."""
    
    def __init__(self):
        """Initialize storage manager."""
        self._current_output_prefix: Optional[str] = None

    @staticmethod
    def _doc_prefix_from_pdf_path(pdf_path: str) -> str:
        normalized = (pdf_path or "").replace("\\\\", "/")
        base = os.path.basename(normalized)
        stem, _ = os.path.splitext(base)
        stem = stem.strip().strip("/").strip("\\")
        return stem or "document"

    def set_current_document(self, pdf_path: str) -> str:
        """Set the blob prefix so one PDF => one output folder in the container."""
        self._current_output_prefix = self._doc_prefix_from_pdf_path(pdf_path)
        return self._current_output_prefix
    
    def read_pdf(self, pdf_path):
        """Read PDF from local file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            io.BytesIO: PDF content as bytes stream
        """
        self.set_current_document(pdf_path)

        pdf_stream = io.BytesIO()
        
        if os.path.isfile(pdf_path):
            logging.info(f"Reading PDF from local file: {pdf_path}")
            with open(pdf_path, 'rb') as f:
                pdf_stream.write(f.read())
            pdf_stream.seek(0)
        else:
            raise ValueError(f"Local file not found: {pdf_path}")
        
        return pdf_stream
    
    def save_image(self, image_data, filename, output_folder=None):
        """Save image to local.
        
        Args:
            image_data: Image bytes
            filename: Name for the saved file
            output_folder: Local folder path (optional)
            
        Returns:
            str: URL or relative path to saved image
        """
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
            local_path = os.path.join(output_folder, filename)
            with open(local_path, 'wb') as f:
                f.write(image_data)
            logging.info(f"Saved image to local file: {local_path}")
            return filename

        logging.warning(f"No output folder specified for {filename}. Skipping save.")
        return None
    
    def save_text(self, content, filename, output_folder=None):
        """Save text content to local.
        
        Args:
            content: Text content to save
            filename: Name for the saved file
            output_folder: Local folder path (optional)
            
        Returns:
            bool: True if saved successfully
        """
        saved = False
        
        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
            local_path = os.path.join(output_folder, filename)
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Saved text to local file: {local_path}")
            saved = True
        
        return saved
