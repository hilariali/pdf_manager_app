import streamlit as st
import os
import tempfile
from pathlib import Path
import zipfile
from utils.pdf_converter import PDFConverter
from utils.pdf_editor import PDFEditor
from utils.pdf_security import PDFSecurity
from utils.ocr_processor import OCRProcessor

# Page configuration
st.set_page_config(
    page_title="PDF Manager Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #e74c3c;
    font-size: 3rem;
    margin-bottom: 2rem;
}
.tool-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    color: white;
    text-align: center;
}
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

class PDFManagerApp:
    def __init__(self):
        self.converter = PDFConverter()
        self.editor = PDFEditor()
        self.security = PDFSecurity()
        self.ocr = OCRProcessor()
        
        # Create temp directory
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def main(self):
        st.markdown('<h1 class="main-header">📄 PDF Manager Pro</h1>', unsafe_allow_html=True)
        st.markdown("### Your Complete PDF Solution")
        
        # Sidebar navigation
        st.sidebar.title("🛠️ Tools")
        tool_category = st.sidebar.selectbox(
            "Select Category",
            ["🔄 Convert", "✏️ Edit", "🔒 Security", "🔍 OCR", "📁 Organize"]
        )
        
        if tool_category == "🔄 Convert":
            self.conversion_tools()
        elif tool_category == "✏️ Edit":
            self.editing_tools()
        elif tool_category == "🔒 Security":
            self.security_tools()
        elif tool_category == "🔍 OCR":
            self.ocr_tools()
        elif tool_category == "📁 Organize":
            self.organization_tools()
    
    def conversion_tools(self):
        st.header("🔄 PDF Conversion Tools")
        
        conversion_type = st.selectbox(
            "Choose conversion type:",
            ["PDF to Word", "PDF to Excel", "PDF to PowerPoint", "PDF to Images", 
             "Word to PDF", "Excel to PDF", "PowerPoint to PDF", "Images to PDF"]
        )
        
        uploaded_file = st.file_uploader(
            "Upload your file",
            type=['pdf', 'docx', 'xlsx', 'pptx', 'jpg', 'jpeg', 'png'],
            help="Drag and drop your file here"
        )
        
        if uploaded_file and st.button("Convert", type="primary"):
            with st.spinner("Converting your file..."):
                try:
                    result = self.converter.convert_file(uploaded_file, conversion_type)
                    if result:
                        st.success("✅ Conversion completed!")
                        st.download_button(
                            label="📥 Download Converted File",
                            data=result['data'],
                            file_name=result['filename'],
                            mime=result['mime_type']
                        )
                except Exception as e:
                    st.error(f"❌ Conversion failed: {str(e)}")
    
    def editing_tools(self):
        st.header("✏️ PDF Editing Tools")
        
        edit_option = st.selectbox(
            "Choose editing option:",
            ["Add Text", "Add Images", "Add Watermark", "Add Page Numbers", 
             "Rotate Pages", "Extract Pages"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if edit_option == "Add Text":
                self.add_text_tool(uploaded_pdf)
            elif edit_option == "Add Images":
                self.add_image_tool(uploaded_pdf)
            elif edit_option == "Add Watermark":
                self.add_watermark_tool(uploaded_pdf)
            elif edit_option == "Add Page Numbers":
                self.add_page_numbers_tool(uploaded_pdf)
            elif edit_option == "Rotate Pages":
                self.rotate_pages_tool(uploaded_pdf)
            elif edit_option == "Extract Pages":
                self.extract_pages_tool(uploaded_pdf)
    
    def security_tools(self):
        st.header("🔒 PDF Security Tools")
        
        security_option = st.selectbox(
            "Choose security option:",
            ["Add Password Protection", "Remove Password", "Digital Signature"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if security_option == "Add Password Protection":
                self.add_password_tool(uploaded_pdf)
            elif security_option == "Remove Password":
                self.remove_password_tool(uploaded_pdf)
            elif security_option == "Digital Signature":
                self.digital_signature_tool(uploaded_pdf)
    
    def ocr_tools(self):
        st.header("🔍 OCR Tools")
        st.info("Convert scanned PDFs and images to searchable, editable text")
        
        uploaded_file = st.file_uploader(
            "Upload scanned PDF or image",
            type=['pdf', 'jpg', 'jpeg', 'png', 'tiff']
        )
        
        if uploaded_file and st.button("Extract Text with OCR", type="primary"):
            with st.spinner("Processing with OCR..."):
                try:
                    result = self.ocr.extract_text(uploaded_file)
                    st.success("✅ OCR processing completed!")
                    
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
                    
                    with st.expander("👁️ Preview Extracted Text"):
                        st.text_area("Extracted Text:", result['text'], height=300)
                        
                except Exception as e:
                    st.error(f"❌ OCR processing failed: {str(e)}")
    
    def organization_tools(self):
        st.header("📁 PDF Organization Tools")
        
        org_option = st.selectbox(
            "Choose organization option:",
            ["Merge PDFs", "Split PDF", "Compress PDF", "Repair PDF"]
        )
        
        if org_option == "Merge PDFs":
            self.merge_pdfs_tool()
        elif org_option == "Split PDF":
            self.split_pdf_tool()
        elif org_option == "Compress PDF":
            self.compress_pdf_tool()
        elif org_option == "Repair PDF":
            self.repair_pdf_tool()
    
    def add_text_tool(self, uploaded_pdf):
        st.subheader("Add Text to PDF")
        
        col1, col2 = st.columns(2)
        with col1:
            text_content = st.text_area("Enter text to add:")
            font_size = st.slider("Font Size", 8, 72, 12)
            text_color = st.color_picker("Text Color", "#000000")
        
        with col2:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            x_position = st.slider("X Position", 0, 600, 100)
            y_position = st.slider("Y Position", 0, 800, 700)
        
        if st.button("Add Text to PDF") and text_content:
            with st.spinner("Adding text..."):
                try:
                    result = self.editor.add_text(
                        uploaded_pdf, text_content, page_number-1, 
                        x_position, y_position, font_size, text_color
                    )
                    st.success("✅ Text added successfully!")
                    st.download_button(
                        label="📥 Download Modified PDF",
                        data=result,
                        file_name=f"text_added_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add text: {str(e)}")
    
    def merge_pdfs_tool(self):
        st.subheader("Merge Multiple PDFs")
        
        uploaded_files = st.file_uploader(
            "Upload PDF files to merge",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if len(uploaded_files) > 1:
            st.info(f"Selected {len(uploaded_files)} files for merging")
            
            # Show file order
            st.write("**Merge Order:**")
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name}")
            
            if st.button("Merge PDFs", type="primary"):
                with st.spinner("Merging PDFs..."):
                    try:
                        result = self.editor.merge_pdfs(uploaded_files)
                        st.success("✅ PDFs merged successfully!")
                        st.download_button(
                            label="📥 Download Merged PDF",
                            data=result,
                            file_name="merged_document.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to merge PDFs: {str(e)}")
        else:
            st.warning("Please upload at least 2 PDF files to merge")

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
