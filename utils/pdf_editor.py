import io
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
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
        """
        Split PDF into multiple files
        split_type: 'pages' (by page numbers), 'range' (by page ranges), 'size' (by file size)
        """
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
        """
        Rearrange pages in a PDF
        new_order: list of page numbers in desired order (1-indexed)
        """
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
    
    def crop_pages(self, pdf_file, crop_box, page_numbers=None):
        """Crop pages to specified dimensions"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if page_numbers is None:
            page_numbers = list(range(len(doc)))
        
        for page_num in page_numbers:
            if page_num < len(doc):
                page = doc.load_page(page_num)
                page.set_cropbox(fitz.Rect(crop_box))
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def remove_pages(self, pdf_file, page_numbers):
        """Remove specific pages from PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Sort page numbers in descending order to avoid index issues
        page_numbers.sort(reverse=True)
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(doc):
                doc.delete_page(page_num - 1)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
    
    def duplicate_pages(self, pdf_file, page_numbers, insert_after=None):
        """Duplicate specific pages"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(doc):
                page = doc.load_page(page_num - 1)
                
                # Create new page with same content
                new_page = doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.show_pdf_page(new_page.rect, doc, page_num - 1)
                
                # Move to desired position if specified
                if insert_after:
                    doc.move_page(len(doc) - 1, insert_after)
        
        output = io.BytesIO()
        doc.save(output)
        output.seek(0)
        doc.close()
        
        return output.getvalue()
