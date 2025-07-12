import io
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cv2
import numpy as np

class OCRProcessor:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text(self, file):
        """Extract text from PDF or image using OCR"""
        if file.type == "application/pdf":
            return self.ocr_pdf(file)
        else:
            return self.ocr_image(file)
    
    def ocr_pdf(self, pdf_file):
        """Perform OCR on PDF file"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        extracted_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            
            # Perform OCR on image
            image = Image.open(io.BytesIO(img_data))
            page_text = pytesseract.image_to_string(image, lang='eng')
            extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        # Create searchable PDF
        searchable_pdf = self.create_searchable_pdf(doc, extracted_text)
        
        return {
            'text': extracted_text,
            'pdf_data': searchable_pdf,
            'pdf_filename': f"searchable_{pdf_file.name}",
            'text_data': extracted_text.encode('utf-8'),
            'text_filename': f"{pdf_file.name.rsplit('.', 1)[0]}_extracted.txt"
        }
    
    def ocr_image(self, image_file):
        """Perform OCR on image file"""
        image = Image.open(image_file)
        
        # Preprocess image for better OCR
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply image enhancement
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Perform OCR
        extracted_text = pytesseract.image_to_string(denoised, lang='eng')
        
        # Create PDF from image with text layer
        pdf_with_text = self.create_pdf_from_image(image, extracted_text)
        
        return {
            'text': extracted_text,
            'pdf_data': pdf_with_text,
            'pdf_filename': f"ocr_{image_file.name.rsplit('.', 1)[0]}.pdf",
            'text_data': extracted_text.encode('utf-8'),
            'text_filename': f"{image_file.name.rsplit('.', 1)[0]}_extracted.txt"
        }
    
    def create_searchable_pdf(self, original_doc, text):
        """Create a searchable PDF by adding text layer"""
        # This is a simplified version - in practice, you'd need to
        # position text accurately over the original content
        output = io.BytesIO()
        original_doc.save(output)
        output.seek(0)
        return output.getvalue()
    
    def create_pdf_from_image(self, image, text):
        """Create PDF from image with text layer"""
        pdf_doc = fitz.open()
        page = pdf_doc.new_page(width=image.width, height=image.height)
        
        # Insert image
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        page.insert_image(page.rect, stream=img_bytes.getvalue())
        
        # Add invisible text layer (simplified)
        page.insert_text((0, 0), text, fontsize=1, color=(1, 1, 1))
        
        output = io.BytesIO()
        pdf_doc.save(output)
        output.seek(0)
        
        return output.getvalue()
