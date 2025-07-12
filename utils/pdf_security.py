import io
import fitz  # PyMuPDF
from cryptography.fernet import Fernet

class PDFSecurity:
    def __init__(self):
        pass
    
    def add_password(self, pdf_file, user_password, owner_password=None):
        """Add password protection to PDF"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        if owner_password is None:
            owner_password = user_password
        
        # Set permissions
        permissions = (
            fitz.PDF_PERM_PRINT |
            fitz.PDF_PERM_COPY |
            fitz.PDF_PERM_ANNOTATE
        )
        
        output = io.BytesIO()
        doc.save(
            output,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=user_password,
            owner_pw=owner_password,
            permissions=permissions
        )
        output.seek(0)
        
        return output.getvalue()
    
    def remove_password(self, pdf_file, password):
        """Remove password protection from PDF"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            if doc.needs_pass:
                if not doc.authenticate(password):
                    raise ValueError("Incorrect password")
            
            output = io.BytesIO()
            doc.save(output, encryption=fitz.PDF_ENCRYPT_NONE)
            output.seek(0)
            
            return output.getvalue()
        except Exception as e:
            raise ValueError(f"Failed to remove password: {str(e)}")
    
    def compress_pdf(self, pdf_file, compression_level="medium"):
        """Compress PDF file to reduce size"""
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Compression settings
        compression_settings = {
            "low": {"deflate": 1, "deflate_images": False},
            "medium": {"deflate": 6, "deflate_images": True},
            "high": {"deflate": 9, "deflate_images": True, "garbage": 4}
        }
        
        settings = compression_settings.get(compression_level, compression_settings["medium"])
        
        output = io.BytesIO()
        doc.save(output, **settings)
        output.seek(0)
        
        return output.getvalue()
