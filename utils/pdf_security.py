import io
import fitz  # PyMuPDF
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import hashlib
from datetime import datetime

class PDFSecurity:
    def __init__(self):
        self.encryption_methods = {
            'AES_128': fitz.PDF_ENCRYPT_AES_128,
            'AES_256': fitz.PDF_ENCRYPT_AES_256,
            'RC4_40': fitz.PDF_ENCRYPT_RC4_40,
            'RC4_128': fitz.PDF_ENCRYPT_RC4_128
        }
        
        self.permission_flags = {
            'print': fitz.PDF_PERM_PRINT,
            'copy': fitz.PDF_PERM_COPY,
            'annotate': fitz.PDF_PERM_ANNOTATE,
            'form': fitz.PDF_PERM_FORM,
            'accessibility': fitz.PDF_PERM_ACCESSIBILITY,
            'assemble': fitz.PDF_PERM_ASSEMBLE,
            'print_high': fitz.PDF_PERM_PRINT_HQ
        }
    
    def add_password(self, pdf_file, user_password, owner_password=None, 
                    encryption_method='AES_256', permissions=None):
        """
        Add password protection to PDF with customizable permissions
        
        Args:
            pdf_file: Uploaded PDF file
            user_password: Password for opening the document
            owner_password: Password for full access (optional)
            encryption_method: Encryption type ('AES_256', 'AES_128', etc.)
            permissions: List of allowed permissions
        """
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            if owner_password is None:
                owner_password = user_password
            
            # Set default permissions if none provided
            if permissions is None:
                permissions = ['print', 'copy', 'annotate']
            
            # Calculate permission flags
            perm_flags = 0
            for perm in permissions:
                if perm in self.permission_flags:
                    perm_flags |= self.permission_flags[perm]
            
            # Get encryption method
            encrypt_method = self.encryption_methods.get(encryption_method, fitz.PDF_ENCRYPT_AES_256)
            
            output = io.BytesIO()
            doc.save(
                output,
                encryption=encrypt_method,
                user_pw=user_password,
                owner_pw=owner_password,
                permissions=perm_flags
            )
            output.seek(0)
            doc.close()
            
            return {
                'data': output.getvalue(),
                'filename': f"protected_{pdf_file.name}",
                'encryption_info': {
                    'method': encryption_method,
                    'permissions': permissions,
                    'protected_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            raise ValueError(f"Failed to add password protection: {str(e)}")
    
    def remove_password(self, pdf_file, password):
        """Remove password protection from PDF"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            if doc.needs_pass:
                if not doc.authenticate(password):
                    raise ValueError("Incorrect password provided")
            
            output = io.BytesIO()
            doc.save(output, encryption=fitz.PDF_ENCRYPT_NONE)
            output.seek(0)
            doc.close()
            
            return {
                'data': output.getvalue(),
                'filename': f"unlocked_{pdf_file.name}",
                'status': 'Password removed successfully'
            }
            
        except Exception as e:
            raise ValueError(f"Failed to remove password: {str(e)}")
    
    def check_pdf_security(self, pdf_file, password=None):
        """Check PDF security status and permissions"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            security_info = {
                'is_encrypted': doc.is_encrypted,
                'needs_password': doc.needs_pass,
                'is_authenticated': False,
                'permissions': {},
                'metadata': {}
            }
            
            if doc.needs_pass and password:
                security_info['is_authenticated'] = doc.authenticate(password)
            elif not doc.needs_pass:
                security_info['is_authenticated'] = True
            
            if security_info['is_authenticated']:
                # Get permissions
                security_info['permissions'] = {
                    'can_print': doc.permissions & fitz.PDF_PERM_PRINT != 0,
                    'can_copy': doc.permissions & fitz.PDF_PERM_COPY != 0,
                    'can_annotate': doc.permissions & fitz.PDF_PERM_ANNOTATE != 0,
                    'can_form': doc.permissions & fitz.PDF_PERM_FORM != 0,
                    'can_accessibility': doc.permissions & fitz.PDF_PERM_ACCESSIBILITY != 0,
                    'can_assemble': doc.permissions & fitz.PDF_PERM_ASSEMBLE != 0,
                    'can_print_hq': doc.permissions & fitz.PDF_PERM_PRINT_HQ != 0
                }
                
                # Get metadata
                security_info['metadata'] = {
                    'page_count': len(doc),
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'subject': doc.metadata.get('subject', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'producer': doc.metadata.get('producer', ''),
                    'creation_date': doc.metadata.get('creationDate', ''),
                    'modification_date': doc.metadata.get('modDate', '')
                }
            
            doc.close()
            return security_info
            
        except Exception as e:
            raise ValueError(f"Failed to check PDF security: {str(e)}")
    
    def compress_pdf(self, pdf_file, compression_level="medium", image_quality=85):
        """
        Compress PDF file to reduce size with various optimization options
        
        Args:
            pdf_file: Uploaded PDF file
            compression_level: 'low', 'medium', 'high', or 'maximum'
            image_quality: JPEG quality for images (1-100)
        """
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            # Compression settings based on level
            compression_settings = {
                "low": {
                    "deflate": 1, 
                    "deflate_images": False,
                    "garbage": 1
                },
                "medium": {
                    "deflate": 6, 
                    "deflate_images": True,
                    "garbage": 2,
                    "clean": True
                },
                "high": {
                    "deflate": 9, 
                    "deflate_images": True,
                    "garbage": 3,
                    "clean": True,
                    "sanitize": True
                },
                "maximum": {
                    "deflate": 9,
                    "deflate_images": True,
                    "garbage": 4,
                    "clean": True,
                    "sanitize": True,
                    "ascii": True
                }
            }
            
            settings = compression_settings.get(compression_level, compression_settings["medium"])
            
            # Get original file size
            original_size = len(pdf_file.getvalue())
            
            output = io.BytesIO()
            doc.save(output, **settings)
            output.seek(0)
            
            compressed_data = output.getvalue()
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            doc.close()
            
            return {
                'data': compressed_data,
                'filename': f"compressed_{pdf_file.name}",
                'compression_info': {
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': round(compression_ratio, 2),
                    'compression_level': compression_level
                }
            }
            
        except Exception as e:
            raise ValueError(f"Failed to compress PDF: {str(e)}")
    
    def add_digital_signature(self, pdf_file, signature_text, position=(100, 100), page_num=0):
        """Add a simple digital signature to PDF"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            if page_num < len(doc):
                page = doc.load_page(page_num)
                
                # Create signature text with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                full_signature = f"{signature_text}\nSigned on: {timestamp}"
                
                # Add signature text
                page.insert_text(
                    position,
                    full_signature,
                    fontsize=10,
                    color=(0, 0, 1),  # Blue color
                    fontname="helv-bo"
                )
                
                # Add signature box
                rect = fitz.Rect(position[0]-5, position[1]-15, position[0]+200, position[1]+30)
                page.draw_rect(rect, color=(0, 0, 1), width=1)
            
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            doc.close()
            
            return {
                'data': output.getvalue(),
                'filename': f"signed_{pdf_file.name}",
                'signature_info': {
                    'signer': signature_text,
                    'timestamp': timestamp,
                    'page': page_num + 1
                }
            }
            
        except Exception as e:
            raise ValueError(f"Failed to add digital signature: {str(e)}")
    
    def redact_content(self, pdf_file, redaction_areas, page_num=0):
        """
        Redact (black out) specific areas of a PDF page
        
        Args:
            pdf_file: Uploaded PDF file
            redaction_areas: List of tuples [(x1, y1, x2, y2), ...]
            page_num: Page number to redact (0-indexed)
        """
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            
            if page_num < len(doc):
                page = doc.load_page(page_num)
                
                for area in redaction_areas:
                    x1, y1, x2, y2 = area
                    rect = fitz.Rect(x1, y1, x2, y2)
                    
                    # Add redaction annotation
                    redact_annot = page.add_redact_annot(rect)
                    redact_annot.set_colors({"stroke": [0, 0, 0], "fill": [0, 0, 0]})
                    redact_annot.update()
                
                # Apply redactions
                page.apply_redactions()
            
            output = io.BytesIO()
            doc.save(output)
            output.seek(0)
            doc.close()
            
            return {
                'data': output.getvalue(),
                'filename': f"redacted_{pdf_file.name}",
                'redaction_info': {
                    'areas_redacted': len(redaction_areas),
                    'page': page_num + 1
                }
            }
            
        except Exception as e:
            raise ValueError(f"Failed to redact content: {str(e)}")
    
    def generate_file_hash(self, pdf_file, algorithm='sha256'):
        """Generate hash for PDF file integrity verification"""
        try:
            hash_algorithms = {
                'md5': hashlib.md5,
                'sha1': hashlib.sha1,
                'sha256': hashlib.sha256,
                'sha512': hashlib.sha512
            }
            
            if algorithm not in hash_algorithms:
                algorithm = 'sha256'
            
            hash_func = hash_algorithms[algorithm]()
            
            # Read file content
            content = pdf_file.read()
            hash_func.update(content)
            
            file_hash = hash_func.hexdigest()
            
            return {
                'hash': file_hash,
                'algorithm': algorithm,
                'file_size': len(content),
                'filename': pdf_file.name
            }
            
        except Exception as e:
            raise ValueError(f"Failed to generate file hash: {str(e)}")
