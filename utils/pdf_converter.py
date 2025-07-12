import io
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import pandas as pd
from docx import Document
from pptx import Presentation
import zipfile

class PDFConverter:
    def __init__(self):
        self.supported_formats = {
            'pdf_to_word': self.pdf_to_word,
            'pdf_to_excel': self.pdf_to_excel,
            'pdf_to_powerpoint': self.pdf_to_powerpoint,
            'pdf_to_images': self.pdf_to_images,
            'word_to_pdf': self.word_to_pdf,
            'excel_to_pdf': self.excel_to_pdf,
            'powerpoint_to_pdf': self.powerpoint_to_pdf,
            'images_to_pdf': self.images_to_pdf
        }
    
    def convert_file(self, uploaded_file, conversion_type):
        """Main conversion dispatcher"""
        conversion_key = conversion_type.lower().replace(' ', '_')
        
        if conversion_key in self.supported_formats:
            return self.supported_formats[conversion_key](uploaded_file)
        else:
            raise ValueError(f"Unsupported conversion type: {conversion_type}")
    
    def pdf_to_word(self, pdf_file):
        """Convert PDF to Word document"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        word_doc = Document()
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            word_doc.add_paragraph(text)
            word_doc.add_page_break()
        
        output = io.BytesIO()
        word_doc.save(output)
        output.seek(0)
        
        return {
            'data': output.getvalue(),
            'filename': f"{Path(pdf_file.name).stem}.docx",
            'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
    
    def pdf_to_images(self, pdf_file):
        """Convert PDF pages to images"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            img_data = pix.tobytes("png")
            images.append(img_data)
        
        # Create ZIP file with all images
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, img_data in enumerate(images):
                zip_file.writestr(f"page_{i+1}.png", img_data)
        
        zip_buffer.seek(0)
        
        return {
            'data': zip_buffer.getvalue(),
            'filename': f"{Path(pdf_file.name).stem}_images.zip",
            'mime_type': 'application/zip'
        }
    
    def images_to_pdf(self, image_files):
        """Convert multiple images to a single PDF"""
        if not isinstance(image_files, list):
            image_files = [image_files]
        
        pdf_document = fitz.open()
        
        for image_file in image_files:
            img = Image.open(image_file)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            img_doc = fitz.open(stream=img_bytes.getvalue(), filetype="png")
            pdf_page = pdf_document.new_page(width=img.width, height=img.height)
            pdf_page.insert_image(pdf_page.rect, stream=img_bytes.getvalue())
        
        output = io.BytesIO()
        pdf_document.save(output)
        output.seek(0)
        
        return {
            'data': output.getvalue(),
            'filename': "converted_images.pdf",
            'mime_type': 'application/pdf'
        }
