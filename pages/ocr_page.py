import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui_components import UIComponents
from utils.ocr_processor import OCRProcessor
from config.settings import OCR_CONFIG

def render():
    """Render the OCR tools page"""
    ui_components = UIComponents()
    ocr = OCRProcessor()
    
    st.header("🔍 OCR Tools")
    st.info("Convert scanned PDFs and images to searchable, editable text using Optical Character Recognition")
    
    # OCR operation type
    ocr_operation = st.selectbox(
        "Choose OCR operation:",
        ["Extract Text from Document", "Create Searchable PDF", "Batch OCR Processing", "OCR with Language Detection"]
    )
    
    if ocr_operation == "Extract Text from Document":
        _render_text_extraction_tool(ui_components, ocr)
    elif ocr_operation == "Create Searchable PDF":
        _render_searchable_pdf_tool(ui_components, ocr)
    elif ocr_operation == "Batch OCR Processing":
        _render_batch_ocr_tool(ui_components, ocr)
    elif ocr_operation == "OCR with Language Detection":
        _render_language_detection_tool(ui_components, ocr)

def _render_text_extraction_tool(ui_components, ocr):
    """Render text extraction tool"""
    st.subheader("📄 Extract Text from Document")
    
    uploaded_file = ui_components.render_file_uploader(
        "Upload scanned PDF or image",
        ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'],
        help_text="Supports PDF, JPG, PNG, TIFF, and BMP files"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### ⚙️ OCR Settings")
            ocr_language = st.selectbox(
                "Document Language",
                OCR_CONFIG['languages'],
                index=0,
                help="Select the primary language in your document for better accuracy"
            )
            
            # Language descriptions
            language_names = {
                'eng': 'English', 'fra': 'French', 'deu': 'German', 'spa': 'Spanish',
                'ita': 'Italian', 'por': 'Portuguese', 'rus': 'Russian', 
                'chi_sim': 'Chinese (Simplified)', 'chi_tra': 'Chinese (Traditional)',
                'jpn': 'Japanese', 'kor': 'Korean'
            }
            st.info(f"🌐 **Selected**: {language_names.get(ocr_language, ocr_language)}")
            
            # Advanced OCR options
            with st.expander("🔧 Advanced Options"):
                enhance_image = st.checkbox("Enhance image quality", value=True, help="Apply image preprocessing for better OCR")
                extract_tables = st.checkbox("Detect tables", value=False, help="Attempt to preserve table structure")
                confidence_threshold = st.slider("Confidence threshold", 0, 100, 60, help="Minimum confidence for text recognition")
        
        with col2:
            st.write("### 📋 Output Options")
            output_format = st.multiselect(
                "Output formats",
                ["Plain Text", "Formatted Text", "JSON", "CSV (for tables)"],
                default=["Plain Text", "Formatted Text"],
                help="Choose how you want the extracted text formatted"
            )
            
            preserve_layout = st.checkbox("Preserve layout", value=True, help="Maintain original text positioning")
            include_confidence = st.checkbox("Include confidence scores", value=False, help="Show OCR confidence for each word")
        
        # File preview
        if uploaded_file.type.startswith('image/'):
            with st.expander("🖼️ Image Preview"):
                st.image(uploaded_file, caption="Uploaded Image", width=400)
        
        if st.button("🚀 Extract Text with OCR", type="primary"):
            with st.spinner("Processing with OCR... This may take a few moments."):
                try:
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🔍 Analyzing document...")
                    progress_bar.progress(25)
                    
                    result = ocr.extract_text(uploaded_file)
                    
                    progress_bar.progress(75)
                    status_text.text("📝 Processing extracted text...")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ OCR processing completed!")
                    
                    st.success("🎉 Text extraction completed successfully!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Searchable PDF",
                            data=result['pdf_data'],
                            file_name=result['pdf_filename'],
                            mime="application/pdf"
                        )
                    
                    with col2:
                        st.download_button(
                            label="📄 Download Text File",
                            data=result['text_data'],
                            file_name=result['text_filename'],
                            mime="text/plain"
                        )
                    
                    # Text preview and statistics
                    _display_ocr_results(result['text'], include_confidence)
                    
                except Exception as e:
                    st.error(f"❌ OCR processing failed: {str(e)}")
                finally:
                    # Clean up progress indicators
                    progress_bar.empty()
                    status_text.empty()

def _render_searchable_pdf_tool(ui_components, ocr):
    """Render searchable PDF creation tool"""
    st.subheader("🔍 Create Searchable PDF")
    st.info("Convert scanned PDFs to searchable documents while preserving the original appearance")
    
    uploaded_pdf = ui_components.render_file_uploader(
        "Upload scanned PDF",
        ['pdf'],
        help_text="Upload a PDF with scanned pages to make it searchable"
    )
    
    if uploaded_pdf:
        col1, col2 = st.columns(2)
        
        with col1:
            ocr_language = st.selectbox("Document Language", OCR_CONFIG['languages'], index=0)
            
            # PDF processing options
            st.write("### 📄 Processing Options")
            process_all_pages = st.checkbox("Process all pages", value=True)
            
            if not process_all_pages:
                page_range = st.text_input("Page range (e.g., 1-5,8,10-12)", "1-5")
            
            preserve_images = st.checkbox("Preserve image quality", value=True)
        
        with col2:
            st.write("### ⚡ Performance Settings")
            processing_quality = st.selectbox(
                "Processing quality",
                ["Fast", "Balanced", "High Quality"],
                index=1,
                help="Higher quality takes longer but provides better results"
            )
            
            parallel_processing = st.checkbox("Enable parallel processing", value=True, help="Process multiple pages simultaneously")
        
        if st.button("🔄 Create Searchable PDF", type="primary"):
            with st.spinner("Creating searchable PDF..."):
                try:
                    result = ocr.extract_text(uploaded_pdf)
                    
                    st.success("✅ Searchable PDF created successfully!")
                    
                    ui_components.render_success_download(
                        result['pdf_data'],
                        result['pdf_filename'],
                        "📥 Download Searchable PDF"
                    )
