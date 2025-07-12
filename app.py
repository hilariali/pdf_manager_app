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
            ["🔄 Convert", "✏️ Edit", "📁 Organize", "🎨 Annotate", "🔒 Security", "🔍 OCR"]
        )
        
        if tool_category == "🔄 Convert":
            self.conversion_tools()
        elif tool_category == "✏️ Edit":
            self.editing_tools()
        elif tool_category == "📁 Organize":
            self.organization_tools()
        elif tool_category == "🎨 Annotate":
            self.annotation_tools()
        elif tool_category == "🔒 Security":
            self.security_tools()
        elif tool_category == "🔍 OCR":
            self.ocr_tools()
    
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
            ["Add Text", "Add Images", "Add Watermark", "Add Page Numbers"]
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
    
    def organization_tools(self):
        st.header("📁 PDF Organization Tools")
        
        org_option = st.selectbox(
            "Choose organization option:",
            ["Merge PDFs", "Split PDF", "Rearrange Pages", "Extract Pages", 
             "Rotate Pages", "Remove Pages", "Duplicate Pages", "Crop Pages"]
        )
        
        if org_option == "Merge PDFs":
            self.merge_pdfs_tool()
        elif org_option == "Split PDF":
            self.split_pdf_tool()
        elif org_option == "Rearrange Pages":
            self.rearrange_pages_tool()
        elif org_option == "Extract Pages":
            self.extract_pages_tool()
        elif org_option == "Rotate Pages":
            self.rotate_pages_tool()
        elif org_option == "Remove Pages":
            self.remove_pages_tool()
        elif org_option == "Duplicate Pages":
            self.duplicate_pages_tool()
        elif org_option == "Crop Pages":
            self.crop_pages_tool()
    
    def annotation_tools(self):
        st.header("🎨 PDF Annotation Tools")
        
        annotation_type = st.selectbox(
            "Choose annotation type:",
            ["Highlight Text", "Underline Text", "Strikeout Text", "Squiggly Underline",
             "Add Notes", "Add Text Box", "Add Stamps", "Add Shapes"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if annotation_type == "Highlight Text":
                self.highlight_tool(uploaded_pdf)
            elif annotation_type == "Underline Text":
                self.underline_tool(uploaded_pdf)
            elif annotation_type == "Strikeout Text":
                self.strikeout_tool(uploaded_pdf)
            elif annotation_type == "Squiggly Underline":
                self.squiggly_tool(uploaded_pdf)
            elif annotation_type == "Add Notes":
                self.notes_tool(uploaded_pdf)
            elif annotation_type == "Add Text Box":
                self.text_box_tool(uploaded_pdf)
            elif annotation_type == "Add Stamps":
                self.stamps_tool(uploaded_pdf)
            elif annotation_type == "Add Shapes":
                self.shapes_tool(uploaded_pdf)
    
    def security_tools(self):
        st.header("🔒 PDF Security Tools")
        
        security_option = st.selectbox(
            "Choose security option:",
            ["Add Password Protection", "Remove Password", "Digital Signature", "Compress PDF"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if security_option == "Add Password Protection":
                self.add_password_tool(uploaded_pdf)
            elif security_option == "Remove Password":
                self.remove_password_tool(uploaded_pdf)
            elif security_option == "Digital Signature":
                self.digital_signature_tool(uploaded_pdf)
            elif security_option == "Compress PDF":
                self.compress_pdf_tool(uploaded_pdf)
    
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
    
    # Editing Tool Methods
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
    
    def add_image_tool(self, uploaded_pdf):
        st.subheader("Add Image to PDF")
        
        uploaded_image = st.file_uploader("Upload image", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_image:
            col1, col2 = st.columns(2)
            with col1:
                page_number = st.number_input("Page Number", min_value=1, value=1)
                x_position = st.slider("X Position", 0, 600, 100)
                y_position = st.slider("Y Position", 0, 800, 100)
            
            with col2:
                width = st.number_input("Width (optional)", min_value=0, value=0)
                height = st.number_input("Height (optional)", min_value=0, value=0)
            
            if st.button("Add Image to PDF"):
                with st.spinner("Adding image..."):
                    try:
                        result = self.editor.add_image(
                            uploaded_pdf, uploaded_image, page_number-1,
                            x_position, y_position, 
                            width if width > 0 else None,
                            height if height > 0 else None
                        )
                        st.success("✅ Image added successfully!")
                        st.download_button(
                            label="📥 Download Modified PDF",
                            data=result,
                            file_name=f"image_added_{uploaded_pdf.name}",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to add image: {str(e)}")
    
    def add_watermark_tool(self, uploaded_pdf):
        st.subheader("Add Watermark")
        
        col1, col2 = st.columns(2)
        with col1:
            watermark_text = st.text_input("Watermark Text", "CONFIDENTIAL")
            font_size = st.slider("Font Size", 20, 100, 50)
        
        with col2:
            opacity = st.slider("Opacity", 0.1, 1.0, 0.3)
            rotation = st.slider("Rotation", 0, 360, 45)
        
        if st.button("Add Watermark"):
            with st.spinner("Adding watermark..."):
                try:
                    result = self.editor.add_watermark(
                        uploaded_pdf, watermark_text, opacity, font_size, rotation
                    )
                    st.success("✅ Watermark added successfully!")
                    st.download_button(
                        label="📥 Download Watermarked PDF",
                        data=result,
                        file_name=f"watermarked_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add watermark: {str(e)}")
    
    def add_page_numbers_tool(self, uploaded_pdf):
        st.subheader("Add Page Numbers")
        
        col1, col2 = st.columns(2)
        with col1:
            position = st.selectbox(
                "Position",
                ["bottom_right", "bottom_left", "top_right", "top_left", "bottom_center"]
            )
            font_size = st.slider("Font Size", 8, 24, 12)
        
        with col2:
            start_number = st.number_input("Start Number", min_value=1, value=1)
        
        if st.button("Add Page Numbers"):
            with st.spinner("Adding page numbers..."):
                try:
                    result = self.editor.add_page_numbers(
                        uploaded_pdf, position, font_size, start_number
                    )
                    st.success("✅ Page numbers added successfully!")
                    st.download_button(
                        label="📥 Download Numbered PDF",
                        data=result,
                        file_name=f"numbered_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add page numbers: {str(e)}")
    
    # Organization Tool Methods
    def merge_pdfs_tool(self):
        st.subheader("Merge Multiple PDFs")
        
        uploaded_files = st.file_uploader(
            "Upload PDF files to merge",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if len(uploaded_files) > 1:
            st.info(f"Selected {len(uploaded_files)} files for merging")
            
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
    
    def split_pdf_tool(self):
        st.subheader("Split PDF")
        
        uploaded_pdf = st.file_uploader("Upload PDF to split", type=['pdf'])
        
        if uploaded_pdf:
            split_method = st.selectbox(
                "Choose split method:",
                ["By Page Numbers", "By Page Ranges", "Equal Parts"]
            )
            
            if split_method == "By Page Numbers":
                page_numbers = st.text_input(
                    "Enter page numbers (comma-separated):",
                    placeholder="1,3,5,7"
                )
                
                if st.button("Split PDF") and page_numbers:
                    with st.spinner("Splitting PDF..."):
                        try:
                            result = self.editor.split_pdf(uploaded_pdf, "pages", page_numbers)
                            st.success(f"✅ PDF split into {len(result)} files!")
                            
                            for i, file_data in enumerate(result):
                                st.download_button(
                                    label=f"📥 Download {file_data['filename']}",
                                    data=file_data['data'],
                                    file_name=file_data['filename'],
                                    mime="application/pdf",
                                    key=f"split_{i}"
                                )
                        except Exception as e:
                            st.error(f"❌ Failed to split PDF: {str(e)}")
    
    def rearrange_pages_tool(self):
        st.subheader("Rearrange Pages")
        
        uploaded_pdf = st.file_uploader("Upload PDF to rearrange", type=['pdf'])
        
        if uploaded_pdf:
            new_order = st.text_input(
                "Enter new page order (comma-separated):",
                placeholder="3,1,4,2,5",
                help="Enter page numbers in the order you want them to appear"
            )
            
            if st.button("Rearrange Pages") and new_order:
                with st.spinner("Rearranging pages..."):
                    try:
                        order_list = [int(p.strip()) for p in new_order.split(',')]
                        result = self.editor.rearrange_pages(uploaded_pdf, order_list)
                        st.success("✅ Pages rearranged successfully!")
                        st.download_button(
                            label="📥 Download Rearranged PDF",
                            data=result,
                            file_name=f"rearranged_{uploaded_pdf.name}",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to rearrange pages: {str(e)}")
    
    def extract_pages_tool(self):
        st.subheader("Extract Pages")
        
        uploaded_pdf = st.file_uploader("Upload PDF to extract pages from", type=['pdf'])
        
        if uploaded_pdf:
            page_numbers = st.text_input(
                "Enter page numbers to extract (comma-separated):",
                placeholder="1,3,5,7"
            )
            
            if st.button("Extract Pages") and page_numbers:
                with st.spinner("Extracting pages..."):
                    try:
                        pages_list = [int(p.strip()) for p in page_numbers.split(',')]
                        result = self.editor.extract_pages(uploaded_pdf, pages_list)
                        st.success("✅ Pages extracted successfully!")
                        st.download_button(
                            label="📥 Download Extracted Pages",
                            data=result,
                            file_name=f"extracted_{uploaded_pdf.name}",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to extract pages: {str(e)}")
    
    def rotate_pages_tool(self):
        st.subheader("Rotate Pages")
        
        uploaded_pdf = st.file_uploader("Upload PDF to rotate", type=['pdf'])
        
        if uploaded_pdf:
            col1, col2 = st.columns(2)
            
            with col1:
                rotation_angle = st.selectbox("Rotation angle:", [90, 180, 270, -90])
            
            with col2:
                page_selection = st.selectbox("Pages to rotate:", ["All pages", "Specific pages"])
            
            if page_selection == "Specific pages":
                page_numbers = st.text_input("Enter page numbers (comma-separated):", placeholder="1,3,5")
                pages_list = [int(p.strip()) for p in page_numbers.split(',')] if page_numbers else None
            else:
                pages_list = None
            
            if st.button("Rotate Pages"):
                with st.spinner("Rotating pages..."):
                    try:
                        result = self.editor.rotate_pages(uploaded_pdf, rotation_angle, pages_list)
                        st.success("✅ Pages rotated successfully!")
                        st.download_button(
                            label="📥 Download Rotated PDF",
                            data=result,
                            file_name=f"rotated_{uploaded_pdf.name}",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to rotate pages: {str(e)}")
    
    # Security Tool Methods
    def add_password_tool(self, uploaded_pdf):
        st.subheader("Add Password Protection")
        
        col1, col2 = st.columns(2)
        with col1:
            user_password = st.text_input("User Password", type="password")
            owner_password = st.text_input("Owner Password (optional)", type="password")
        
        with col2:
            encryption_method = st.selectbox("Encryption Method", ["AES_256", "AES_128", "RC4_128"])
            
            permissions = st.multiselect(
                "Permissions",
                ["print", "copy", "annotate", "form", "accessibility"],
                default=["print", "copy"]
            )
        
        if st.button("Add Password Protection") and user_password:
            with st.spinner("Adding password protection..."):
                try:
                    result = self.security.add_password(
                        uploaded_pdf, user_password, owner_password or None,
                        encryption_method, permissions
                    )
                    st.success("✅ Password protection added successfully!")
                    st.download_button(
                        label="📥 Download Protected PDF",
                        data=result['data'],
                        file_name=result['filename'],
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add password protection: {str(e)}")
    
    def remove_password_tool(self, uploaded_pdf):
        st.subheader("Remove Password Protection")
        
        password = st.text_input("Enter PDF Password", type="password")
        
        if st.button("Remove Password") and password:
            with st.spinner("Removing password..."):
                try:
                    result = self.security.remove_password(uploaded_pdf, password)
                    st.success("✅ Password removed successfully!")
                    st.download_button(
                        label="📥 Download Unlocked PDF",
                        data=result['data'],
                        file_name=result['filename'],
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to remove password: {str(e)}")
    
    def compress_pdf_tool(self, uploaded_pdf):
        st.subheader("Compress PDF")
        
        compression_level = st.selectbox(
            "Compression Level",
            ["low", "medium", "high", "maximum"]
        )
        
        if st.button("Compress PDF"):
            with st.spinner("Compressing PDF..."):
                try:
                    result = self.security.compress_pdf(uploaded_pdf, compression_level)
                    st.success("✅ PDF compressed successfully!")
                    
                    # Show compression statistics
                    info = result['compression_info']
                    st.info(f"Original size: {info['original_size']:,} bytes")
                    st.info(f"Compressed size: {info['compressed_size']:,} bytes")
                    st.info(f"Compression ratio: {info['compression_ratio']}%")
                    
                    st.download_button(
                        label="📥 Download Compressed PDF",
                        data=result['data'],
                        file_name=result['filename'],
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to compress PDF: {str(e)}")
    
    def digital_signature_tool(self, uploaded_pdf):
        st.subheader("Add Digital Signature")
        
        col1, col2 = st.columns(2)
        with col1:
            signature_text = st.text_input("Signature Text", "Digitally Signed")
            page_number = st.number_input("Page Number", min_value=1, value=1)
        
        with col2:
            x_position = st.slider("X Position", 0, 600, 100)
            y_position = st.slider("Y Position", 0, 800, 100)
        
        if st.button("Add Digital Signature"):
            with st.spinner("Adding digital signature..."):
                try:
                    result = self.security.add_digital_signature(
                        uploaded_pdf, signature_text, (x_position, y_position), page_number-1
                    )
                    st.success("✅ Digital signature added successfully!")
                    st.download_button(
                        label="📥 Download Signed PDF",
                        data=result['data'],
                        file_name=result['filename'],
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add digital signature: {str(e)}")
    
    # Annotation Tool Methods
    def highlight_tool(self, uploaded_pdf):
        st.subheader("Add Highlights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            highlight_color = st.color_picker("Highlight Color", "#FFFF00")
        
        with col2:
            x1 = st.number_input("X1 Position", value=100)
            y1 = st.number_input("Y1 Position", value=100)
            x2 = st.number_input("X2 Position", value=200)
            y2 = st.number_input("Y2 Position", value=120)
        
        if st.button("Add Highlight"):
            with st.spinner("Adding highlight..."):
                try:
                    result = self.editor.add_highlight(
                        uploaded_pdf, page_number-1, [x1, y1, x2, y2], highlight_color
                    )
                    st.success("✅ Highlight added successfully!")
                    st.download_button(
                        label="📥 Download Highlighted PDF",
                        data=result,
                        file_name=f"highlighted_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add highlight: {str(e)}")
    
    # Add placeholder methods for other annotation tools
    def underline_tool(self, uploaded_pdf):
        st.info("Underline tool - Implementation similar to highlight_tool")
    
    def strikeout_tool(self, uploaded_pdf):
        st.info("Strikeout tool - Implementation similar to highlight_tool")
    
    def squiggly_tool(self, uploaded_pdf):
        st.info("Squiggly tool - Implementation similar to highlight_tool")
    
    def notes_tool(self, uploaded_pdf):
        st.info("Notes tool - Implementation for adding sticky notes")
    
    def text_box_tool(self, uploaded_pdf):
        st.info("Text box tool - Implementation for adding text annotations")
    
    def stamps_tool(self, uploaded_pdf):
        st.info("Stamps tool - Implementation for adding stamps")
    
    def shapes_tool(self, uploaded_pdf):
        st.info("Shapes tool - Implementation for adding geometric shapes")
    
    # Add placeholder methods for other organization tools
    def remove_pages_tool(self):
        st.info("Remove pages tool - Implementation for removing specific pages")
    
    def duplicate_pages_tool(self):
        st.info("Duplicate pages tool - Implementation for duplicating pages")
    
    def crop_pages_tool(self):
        st.info("Crop pages tool - Implementation for cropping pages")

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
