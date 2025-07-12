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
    
    def add_image(self, pdf_file, image_file, page_num, x, y, width=None, height=None):
        """Add image to a specific page of the PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            
            # Open and process image
            img = Image.open(image_file)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Calculate dimensions if not provided
            if width is None:
                width = img.width
            if height is None:
                height = img.height
            
            # Insert image
            rect = fitz.Rect(x, y, x + width, y + height)
            page.insert_image(rect, stream=img_bytes.getvalue())
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_watermark(self, pdf_file, watermark_text, opacity=0.3, font_size=50, rotation=45):
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
    
    def add_page_numbers(self, pdf_file, position="bottom_right", font_size=12, start_number=1):
        """Add page numbers to all pages"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            rect = page.rect
            
            # Calculate position
            if position == "bottom_right":
                x, y = rect.width - 50, rect.height - 30
            elif position == "bottom_left":
                x, y = 30, rect.height - 30
            elif position == "top_right":
                x, y = rect.width - 50, 30
            elif position == "top_left":
                x, y = 30, 30
            elif position == "bottom_center":
                x, y = rect.width/2, rect.height - 30
            else:
                x, y = rect.width - 50, rect.height - 30
            
            # Add page number
            page_text = str(page_num + start_number)
            page.insert_text(
                (x, y),
                page_text,
                fontsize=font_size,
                color=(0, 0, 0),
                fontname="helv"
            )
        
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
    
    def split_pdf(self, pdf_file, split_type="pages", split_value=None):
        """Split PDF into multiple files"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        split_files = []
        
        if split_type == "pages" and split_value:
            # Split by specific page numbers
            page_numbers = [int(p.strip()) for p in split_value.split(',')]
            
            for i, page_num in enumerate(page_numbers):
                if page_num <= len(doc):
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
                    
                    output = io.BytesIO()
                    new_doc.save(output)
                    output.seek(0)
                    
                    split_files.append({
                        'data': output.getvalue(),
                        'filename': f"page_{page_num}.pdf"
                    })
                    new_doc.close()
        
        elif split_type == "range" and split_value:
            # Split by page ranges
            ranges = split_value.split(',')
            for i, range_str in enumerate(ranges):
                if '-' in range_str:
                    start, end = map(int, range_str.split('-'))
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
                    
                    output = io.BytesIO()
                    new_doc.save(output)
                    output.seek(0)
                    
                    split_files.append({
                        'data': output.getvalue(),
                        'filename': f"pages_{start}-{end}.pdf"
                    })
                    new_doc.close()
        
        elif split_type == "equal":
            # Split into equal parts
            pages_per_part = int(split_value) if split_value else 1
            total_pages = len(doc)
            
            for i in range(0, total_pages, pages_per_part):
                end_page = min(i + pages_per_part - 1, total_pages - 1)
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=i, to_page=end_page)
                
                output = io.BytesIO()
                new_doc.save(output)
                output.seek(0)
                
                split_files.append({
                    'data': output.getvalue(),
                    'filename': f"part_{i//pages_per_part + 1}.pdf"
                })
                new_doc.close()
        
        doc.close()
        return split_files
    
    def rearrange_pages(self, pdf_file, new_order):
        """Rearrange pages in a PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        new_doc = fitz.open()
        
        for page_num in new_order:
            if 1 <= page_num <= len(doc):
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
        
        output = io.BytesIO()
        new_doc.save(output)
        output.seek(0)
        doc.close()
        new_doc.close()
        
        return output.getvalue()
    
    def extract_pages(self, pdf_file, page_numbers):
        """Extract specific pages from PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        new_doc = fitz.open()
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(doc):
                new_doc.insert_pdf(doc, from_page=page_num-1, to_page=page_num-1)
        
        output = io.BytesIO()
        new_doc.save(output)
        output.seek(0)
        doc.close()
        new_doc.close()
        
        return output.getvalue()
    
    def rotate_pages(self, pdf_file, rotation_angle, page_numbers=None):
        """Rotate specific pages or all pages"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_numbers is None:
            page_numbers = list(range(1, len(doc) + 1))
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(doc):
                page = doc.load_page(page_num - 1)
                page.set_rotation(rotation_angle)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    # Annotation Methods
    def add_highlight(self, pdf_file, page_num, rect_coords, color="#FFFF00"):
        """Add highlight annotation"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            
            # Convert hex color to RGB
            color_rgb = [int(color[i:i+2], 16)/255.0 for i in (1, 3, 5)]
            
            highlight = page.add_highlight_annot(rect)
            highlight.set_colors({"stroke": color_rgb, "fill": color_rgb})
            highlight.update()
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_underline(self, pdf_file, page_num, rect_coords, color="#FF0000"):
        """Add underline annotation"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            
            color_rgb = [int(color[i:i+2], 16)/255.0 for i in (1, 3, 5)]
            
            underline = page.add_underline_annot(rect)
            underline.set_colors({"stroke": color_rgb})
            underline.update()
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_strikeout(self, pdf_file, page_num, rect_coords, color="#FF0000"):
        """Add strikeout annotation"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            
            color_rgb = [int(color[i:i+2], 16)/255.0 for i in (1, 3, 5)]
            
            strikeout = page.add_strikeout_annot(rect)
            strikeout.set_colors({"stroke": color_rgb})
            strikeout.update()
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_squiggly(self, pdf_file, page_num, rect_coords, color="#00FF00"):
        """Add squiggly underline annotation"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            
            color_rgb = [int(color[i:i+2], 16)/255.0 for i in (1, 3, 5)]
            
            squiggly = page.add_squiggly_annot(rect)
            squiggly.set_colors({"stroke": color_rgb})
            squiggly.update()
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_note(self, pdf_file, page_num, point, content, icon="Note"):
        """Add sticky note annotation"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            
            note = page.add_text_annot(fitz.Point(point), content)
            note.set_info(icon=icon)
            note.update()
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_text_annotation(self, pdf_file, page_num, rect_coords, content, font_size=12):
        """Add text annotation (free text)"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            
            text_annot = page.add_freetext_annot(rect, content, fontsize=font_size)
            text_annot.update()
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_stamp(self, pdf_file, page_num, rect_coords, stamp_text="APPROVED", color="#FF0000"):
        """Add stamp annotation"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            rect = fitz.Rect(rect_coords)
            
            # Create stamp using text
            page.insert_text(
                (rect.x0, rect.y0),
                stamp_text,
                fontsize=20,
                color=tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5)),
                fontname="helv-bo"
            )
            
            # Add border
            page.draw_rect(rect, color=tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5)), width=2)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def add_shape(self, pdf_file, page_num, shape_type, coords, color="#000000", fill_color=None):
        """Add geometric shapes"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_num < len(doc):
            page = doc.load_page(page_num)
            color_rgb = tuple(int(color[i:i+2], 16)/255.0 for i in (1, 3, 5))
            
            if shape_type == "rectangle":
                rect = fitz.Rect(coords)
                if fill_color:
                    fill_rgb = tuple(int(fill_color[i:i+2], 16)/255.0 for i in (1, 3, 5))
                    page.draw_rect(rect, color=color_rgb, fill=fill_rgb, width=2)
                else:
                    page.draw_rect(rect, color=color_rgb, width=2)
            
            elif shape_type == "circle":
                x, y, radius = coords
                point = fitz.Point(x, y)
                if fill_color:
                    fill_rgb = tuple(int(fill_color[i:i+2], 16)/255.0 for i in (1, 3, 5))
                    page.draw_circle(point, radius, color=color_rgb, fill=fill_rgb, width=2)
                else:
                    page.draw_circle(point, radius, color=color_rgb, width=2)
            
            elif shape_type == "line":
                p1, p2 = coords
                page.draw_line(fitz.Point(p1), fitz.Point(p2), color=color_rgb, width=2)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
