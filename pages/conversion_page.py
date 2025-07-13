import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui_components import UIComponents
from utils.pdf_converter import PDFConverter
from config.settings import APP_CONFIG

def render():
    """Render the conversion tools page"""
    ui_components = UIComponents()
    converter = PDFConverter()
    
    st.header("🔄 PDF Conversion Tools")
    
    conversion_type = st.selectbox(
        "Choose conversion type:",
        ["PDF to Word", "PDF to Excel", "PDF to PowerPoint", "PDF to Images", 
         "Word to PDF", "Excel to PDF", "PowerPoint to PDF", "Images to PDF"]
    )
    
    # Determine file types based on conversion
    file_types = _get_file_types_for_conversion(conversion_type)
    
    uploaded_file = ui_components.render_file_uploader(
        "Upload your file",
        file_types,
        help_text="Drag and drop your file here"
    )
    
    if uploaded_file and st.button("Convert", type="primary"):
        with st.spinner("Converting your file..."):
            try:
                result = converter.convert_file(uploaded_file, conversion_type)
                if result:
                    ui_components.render_success_download(
                        result['data'],
                        result['filename'],
                        "📥 Download Converted File",
                        result['mime_type']
                    )
            except Exception as e:
                st.error(f"❌ Conversion failed: {str(e)}")

def _get_file_types_for_conversion(conversion_type):
    """Get appropriate file types based on conversion type"""
    if "PDF to" in conversion_type:
        return APP_CONFIG['supported_formats']['pdf']
    elif "Word to" in conversion_type:
        return ['docx']
    elif "Excel to" in conversion_type:
        return ['xlsx']
    elif "PowerPoint to" in conversion_type:
        return ['pptx']
    elif "Images to" in conversion_type:
        return APP_CONFIG['supported_formats']['images']
    else:
        return APP_CONFIG['supported_formats']['pdf'] + APP_CONFIG['supported_formats']['office'] + APP_CONFIG['supported_formats']['images']
