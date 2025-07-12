"""
PDF Manager Utilities Package

This package contains utility modules for PDF processing operations including:
- PDF conversion between different formats
- PDF editing and manipulation
- Security and protection features
- OCR text extraction
"""

from .pdf_converter import PDFConverter
from .pdf_editor import PDFEditor
from .pdf_security import PDFSecurity
from .ocr_processor import OCRProcessor

__version__ = "1.0.0"
__author__ = "PDF Manager Pro Team"

# Package-level constants
SUPPORTED_PDF_FORMATS = ['pdf']
SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'tiff', 'bmp']
SUPPORTED_OFFICE_FORMATS = ['docx', 'xlsx', 'pptx']

# Default settings
DEFAULT_COMPRESSION_LEVEL = "medium"
DEFAULT_OCR_LANGUAGE = "eng"
DEFAULT_FONT_SIZE = 12
DEFAULT_WATERMARK_OPACITY = 0.3

# File size limits (in bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_BATCH_FILES = 10

__all__ = [
    'PDFConverter',
    'PDFEditor', 
    'PDFSecurity',
    'OCRProcessor',
    'SUPPORTED_PDF_FORMATS',
    'SUPPORTED_IMAGE_FORMATS',
    'SUPPORTED_OFFICE_FORMATS',
    'DEFAULT_COMPRESSION_LEVEL',
    'DEFAULT_OCR_LANGUAGE',
    'DEFAULT_FONT_SIZE',
    'DEFAULT_WATERMARK_OPACITY',
    'MAX_FILE_SIZE',
    'MAX_BATCH_FILES'
]
