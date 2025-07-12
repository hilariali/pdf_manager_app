import io
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
import base64
from datetime import datetime

class PDFEditor:
    def __init__(self):
        self.annotation_types = {
            'highlight': self.add_highlight,
            'underline': self.add_underline,
            'strikeout': self.add_strikeout,
            'squiggly': self.add_squiggly,
            'note': self.add_note,
            'text': self.add_text_annotation,
            'stamp': self.add_stamp,
            'shape': self.add_shape
        }
    
    def get_pdf_preview(self, pdf_file, page_num=0, zoom=1.5):
        """Generate preview image of a PDF page"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            page = doc.load_page(page_num)
            
            # Create pixmap with zoom
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to base64 for display in Streamlit
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()
            
            # Get page info
            page_info = {
                'width': page.rect.width,
                'height': page.rect.height,
                'page_count': len(doc),
                'zoom': zoom
            }
            
            doc.close()
            return img_base64, page_info
            
        except Exception as e:
            raise ValueError(f"Failed to generate preview: {str(e)}")
    
    def get_all_pages_preview(self, pdf_file, max_pages=10):
        """Generate preview thumbnails for multiple pages"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            previews = []
            
            total_pages = min(len(doc), max_pages)
            
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                
                # Create smaller thumbnail
                mat = fitz.Matrix(0.5, 0.5)  # Smaller zoom for thumbnails
                pix = page.get_pixmap(matrix=mat)
                
                img_data = pix.tobytes("png")
                img_base64 = base64.b64encode(img_data).decode()
                
                previews.append({
                    'page_num': page_num + 1,
                    'image': img_base64,
                    'width': page.rect.width,
                    'height': page.rect.height
                })
            
            doc.close()
            return previews
            
        except Exception as e:
            raise ValueError(f"Failed to generate page previews: {str(e)}")
    
    def add_text_with_preview(self, pdf_file, text, pages, x, y, font_size=12, color="#000000"):
        """Add text to multiple pages with preview support"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Convert hex color to RGB
        color_rgb = tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5))
        
        # Apply to selected pages
        for page_num in pages:
            if page_num - 1 < len(doc):
                page = doc.load_page(page_num - 1)
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
        doc.close()
        
        return output.getvalue()
    
    def add_image_with_preview(self, pdf_file, image_file, pages, x, y, width=None, height=None):
        """Add image to multiple pages with preview support"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Process image
        img = Image.open(image_file)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Calculate dimensions if not provided
        if width is None:
            width = img.width
        if height is None:
            height = img.height
        
        # Apply to selected pages
        for page_num in pages:
            if page_num - 1 < len(doc):
                page = doc.load_page(page_num - 1)
                rect = fitz.Rect(x, y, x + width, y + height)
                page.insert_image(rect, stream=img_bytes.getvalue())
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_watermark_with_preview(self, pdf_file, watermark_text, pages, opacity=0.3, font_size=50, rotation=45):
        """Add watermark to multiple pages with preview support"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Apply to selected pages
        for page_num in pages:
            if page_num - 1 < len(doc):
                page = doc.load_page(page_num - 1)
                rect = page.rect
                
                # Add watermark text diagonally across the page
                page.insert_text(
                    (rect.width/2, rect.height/2),
                    watermark_text,
                    fontsize=font_size,
                    color=(0.7, 0.7, 0.7),
                    fontname="helv-bo",
                    rotate=rotation
                )
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def create_preview_with_overlay(self, pdf_file, page_num, overlay_type, overlay_data):
        """Create preview with overlay without modifying the original PDF"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            page = doc.load_page(page_num)
            
            # Create a copy for preview
            preview_doc = fitz.open()
            preview_page = preview_doc.new_page(width=page.rect.width, height=page.rect.height)
            preview_page.show_pdf_page(preview_page.rect, doc, page_num)
            
            # Apply overlay based on type
            if overlay_type == "text":
                text, x, y, font_size, color = overlay_data
                color_rgb = tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5))
                preview_page.insert_text((x, y), text, fontsize=font_size, color=color_rgb, fontname="helv")
            
            elif overlay_type == "watermark":
                text, font_size, rotation = overlay_data
                rect = preview_page.rect
                preview_page.insert_text(
                    (rect.width/2, rect.height/2), text,
                    fontsize=font_size, color=(0.7, 0.7, 0.7),
                    fontname="helv-bo", rotate=rotation
                )
            
            # Generate preview image
            mat = fitz.Matrix(1.5, 1.5)
            pix = preview_page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()
            
            doc.close()
            preview_doc.close()
            
            return img_base64
            
        except Exception as e:
            raise ValueError(f"Failed to create preview: {str(e)}")
    
    # Keep all existing methods from the previous implementation
    def add_text(self, pdf_file, text, page_num, x, y, font_size=12, color="#000000"):
        """Add text to a specific page of the PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            color_rgb = tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5))
            page.insert_text((x, y), text, fontsize=font_size, color=color_rgb, fontname="helv")
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
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
        merged_doc.close()
        
        return output.getvalue()
