"""
Configuration settings for PDF Manager Pro
"""

APP_CONFIG = {
    'app_name': 'PDF Manager Pro',
    'app_version': '1.0.0',
    'app_description': 'Complete PDF Management Solution with Interactive Preview',
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'max_pages_preview': 20,
    'supported_formats': {
        'pdf': ['pdf'],
        'images': ['jpg', 'jpeg', 'png', 'tiff', 'bmp'],
        'office': ['docx', 'xlsx', 'pptx'],
        'text': ['txt']
    }
}

UI_CONFIG = {
    'primary_color': '#e74c3c',
    'secondary_color': '#3498db',
    'success_color': '#27ae60',
    'warning_color': '#f39c12',
    'error_color': '#e74c3c'
}

OCR_CONFIG = {
    'languages': ['eng', 'fra', 'deu', 'spa', 'ita', 'por', 'rus', 'chi_sim', 'jpn', 'kor'],
    'default_language': 'eng',
    'dpi': 300
}

SECURITY_CONFIG = {
    'encryption_methods': ['AES_256', 'AES_128', 'RC4_128'],
    'default_encryption': 'AES_256',
    'permissions': ['print', 'copy', 'annotate', 'form', 'accessibility']
}
