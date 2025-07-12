import io
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

class PDFEditor:
    def __init__(self):
        pass
    
    def add_text(self, pdf_file, text, page_num, x, y, font_size=12, color="#000000"):
        """Add text to a specific page of the PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            
            # Convert hex color to RGB
            color_rgb = tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5))
            
            # Insert text
            page.insert_text(
                (x, y),
                text,
                fontsize=font_size,
                color=color_rgb,
                fontname="helv"
            )
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        
        return output.getvalue()
    
    def add_watermark(self, pdf_file, watermark_text, opacity=0.3):
        """Add watermark to all pages"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Get page dimensions
            rect = page.rect
            
            # Add watermark text diagonally across the page
            page.insert_text(
                (rect.width/2, rect.height/2),
                watermark_text,
                fontsize=50,
                color=(0.7, 0.7, 0.7),
                fontname="helv-bo",
                rotate=45
            )
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        
        return output.getvalue()
    
    def merge_pdfs(self, pdf_files):
        """Merge multiple PDF files into one"""
        merged_doc = fitz.open()
        
        for pdf_file in pdf_files:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            merged_doc.insert_pdf(doc)
            doc.close()
        
        output = io.BytesIO()
        merged_doc.save(output)
        output.seek(0)
        
        return output.getvalue()
    
    def split_pdf(self, pdf_file, page_ranges):
        """Split PDF into multiple files based on page ranges"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        split_files = []
        
        for start, end in page_ranges:
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
            
            output = io.BytesIO()
            new_doc.save(output)
            output.seek(0)
            
            split_files.append({
                'data': output.getvalue(),
                'filename': f"split_{start}-{end}.pdf"
            })
            new_doc.close()
        
        return split_files
    
    def rotate_pages(self, pdf_file, rotation_angle, page_numbers=None):
        """Rotate specific pages or all pages"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_numbers is None:
            page_numbers = list(range(len(doc)))
        
        for page_num in page_numbers:
            if page_num < len(doc):
                page = doc.load_page(page_num)
                page.set_rotation(rotation_angle)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        
        return output.getvalue()
