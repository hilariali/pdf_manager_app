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

# Enhanced CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #e74c3c;
    font-size: 3rem;
    margin-bottom: 2rem;
}

.pdf-preview-container {
    border: 2px solid #e1e8ed;
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
    background: #f8f9fa;
    position: relative;
}

.before-after-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 20px 0;
}

.preview-section {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

class PDFManagerApp:
    def __init__(self):
        self.converter = PDFConverter()
        self.editor = PDFEditor()
        self.security = PDFSecurity()
        self.ocr = OCRProcessor()
        
        # Initialize session state
        if 'selected_pages' not in st.session_state:
            st.session_state.selected_pages = []
        if 'position_x' not in st.session_state:
            st.session_state.position_x = 100
        if 'position_y' not in st.session_state:
            st.session_state.position_y = 100
        
        # Create temp directory
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def main(self):
        st.markdown('<h1 class="main-header">📄 PDF Manager Pro</h1>', unsafe_allow_html=True)
        st.markdown("### Your Complete PDF Solution with Interactive Preview")
        
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
    
    def render_page_selector(self, pdf_file, max_pages=None):
        """Render interactive page selector with thumbnails"""
        st.subheader("📄 Select Pages")
        
        try:
            # Get page previews
            previews = self.editor.get_all_pages_preview(pdf_file, max_pages or 20)
            
            # Page selection options
            selection_mode = st.radio(
                "Page Selection:",
                ["All Pages", "Specific Pages", "Page Range"],
                horizontal=True
            )
            
            if selection_mode == "All Pages":
                st.session_state.selected_pages = list(range(1, len(previews) + 1))
                st.success(f"Selected all {len(previews)} pages")
                
            elif selection_mode == "Specific Pages":
                st.write("Click on page thumbnails to select/deselect:")
                
                # Create thumbnail grid
                cols = st.columns(5)
                for i, preview in enumerate(previews):
                    with cols[i % 5]:
                        page_num = preview['page_num']
                        
                        # Create clickable thumbnail
                        if st.button(
                            f"Page {page_num}",
                            key=f"page_{page_num}",
                            help=f"Click to toggle selection of page {page_num}"
                        ):
                            if page_num in st.session_state.selected_pages:
                                st.session_state.selected_pages.remove(page_num)
                            else:
                                st.session_state.selected_pages.append(page_num)
                        
                        # Display thumbnail
                        st.image(
                            f"data:image/png;base64,{preview['image']}",
                            caption=f"Page {page_num}",
                            width=100
                        )
                        
                        # Show selection status
                        if page_num in st.session_state.selected_pages:
                            st.success("✓ Selected")
                        else:
                            st.info("Click to select")
                
                st.write(f"Selected pages: {sorted(st.session_state.selected_pages)}")
                
            elif selection_mode == "Page Range":
                col1, col2 = st.columns(2)
                with col1:
                    start_page = st.number_input("Start Page", min_value=1, max_value=len(previews), value=1)
                with col2:
                    end_page = st.number_input("End Page", min_value=start_page, max_value=len(previews), value=len(previews))
                
                st.session_state.selected_pages = list(range(start_page, end_page + 1))
                st.info(f"Selected pages {start_page} to {end_page}")
            
            return st.session_state.selected_pages
            
        except Exception as e:
            st.error(f"Failed to load page previews: {str(e)}")
            return [1]
    
    def render_position_selector(self, pdf_file, page_num=0):
        """Render interactive position selector"""
        st.subheader("🎯 Position Selection")
        
        try:
            # Get PDF preview
            preview_img, page_info = self.editor.get_pdf_preview(pdf_file, page_num)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**PDF Preview:**")
                st.image(f"data:image/png;base64,{preview_img}", caption=f"Page {page_num + 1}", width=600)
            
            with col2:
                st.write("**Position Controls:**")
                
                # Manual position input
                new_x = st.number_input(
                    "X Position", 
                    min_value=0, 
                    max_value=int(page_info['width']), 
                    value=st.session_state.position_x,
                    key="pos_x"
                )
                
                new_y = st.number_input(
                    "Y Position", 
                    min_value=0, 
                    max_value=int(page_info['height']), 
                    value=st.session_state.position_y,
                    key="pos_y"
                )
                
                # Update session state
                st.session_state.position_x = new_x
                st.session_state.position_y = new_y
                
                # Quick position presets
                st.write("**Quick Positions:**")
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button("Top Left"):
                        st.session_state.position_x = 50
                        st.session_state.position_y = 50
                        st.rerun()
                    
                    if st.button("Center"):
                        st.session_state.position_x = int(page_info['width'] / 2)
                        st.session_state.position_y = int(page_info['height'] / 2)
                        st.rerun()
                
                with col_b:
                    if st.button("Top Right"):
                        st.session_state.position_x = int(page_info['width'] - 100)
                        st.session_state.position_y = 50
                        st.rerun()
                    
                    if st.button("Bottom Right"):
                        st.session_state.position_x = int(page_info['width'] - 100)
                        st.session_state.position_y = int(page_info['height'] - 50)
                        st.rerun()
                
                # Page info
                st.info(f"Page size: {int(page_info['width'])} × {int(page_info['height'])} pts")
            
            return st.session_state.position_x, st.session_state.position_y
            
        except Exception as e:
            st.error(f"Failed to load preview: {str(e)}")
            return 100, 100
    
    def render_before_after_preview(self, pdf_file, page_num, overlay_type, overlay_data):
        """Render before and after preview"""
        try:
            # Get original preview
            original_preview, _ = self.editor.get_pdf_preview(pdf_file, page_num)
            
            # Get preview with overlay
            modified_preview = self.editor.create_preview_with_overlay(
                pdf_file, page_num, overlay_type, overlay_data
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📄 Before")
                st.image(f"data:image/png;base64,{original_preview}", caption="Original", use_column_width=True)
            
            with col2:
                st.markdown("#### ✨ After")
                st.image(f"data:image/png;base64,{modified_preview}", caption="Modified", use_column_width=True)
            
        except Exception as e:
            st.error(f"Failed to generate preview: {str(e)}")
    
    # CONVERSION TOOLS
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
    
    # EDITING TOOLS WITH PREVIEW
    def editing_tools(self):
        st.header("✏️ PDF Editing Tools with Interactive Preview")
        
        edit_option = st.selectbox(
            "Choose editing option:",
            ["Add Text", "Add Images", "Add Watermark", "Add Page Numbers"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if edit_option == "Add Text":
                self.add_text_tool_enhanced(uploaded_pdf)
            elif edit_option == "Add Images":
                self.add_image_tool_enhanced(uploaded_pdf)
            elif edit_option == "Add Watermark":
                self.add_watermark_tool_enhanced(uploaded_pdf)
            elif edit_option == "Add Page Numbers":
                self.add_page_numbers_tool(uploaded_pdf)
    
    def add_text_tool_enhanced(self, uploaded_pdf):
        st.subheader("Add Text to PDF with Interactive Preview")
        
        # Page selection
        selected_pages = self.render_page_selector(uploaded_pdf)
        
        if not selected_pages:
            st.warning("Please select at least one page")
            return
        
        # Text configuration
        col1, col2 = st.columns(2)
        
        with col1:
            text_content = st.text_area("Enter text to add:", height=100)
            font_size = st.slider("Font Size", 8, 72, 12)
            text_color = st.color_picker("Text Color", "#000000")
        
        with col2:
            # Preview page selector
            preview_page = st.selectbox(
                "Preview Page:",
                selected_pages,
                index=0,
                format_func=lambda x: f"Page {x}"
            ) - 1
        
        if text_content:
            # Position selection with preview
            x_pos, y_pos = self.render_position_selector(uploaded_pdf, preview_page)
            
            # Live preview
            st.subheader("🔍 Live Preview")
            self.render_before_after_preview(
                uploaded_pdf, 
                preview_page, 
                "text", 
                (text_content, x_pos, y_pos, font_size, text_color)
            )
            
            # Apply button
            if st.button("Apply Text to Selected Pages", type="primary"):
                with st.spinner("Adding text to selected pages..."):
                    try:
                        result = self.editor.add_text_with_preview(
                            uploaded_pdf, text_content, selected_pages,
                            x_pos, y_pos, font_size, text_color
                        )
                        st.success(f"✅ Text added to {len(selected_pages)} pages successfully!")
                        st.download_button(
                            label="📥 Download Modified PDF",
                            data=result,
                            file_name=f"text_added_{uploaded_pdf.name}",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to add text: {str(e)}")
    
    def add_image_tool_enhanced(self, uploaded_pdf):
        st.subheader("Add Image to PDF with Interactive Preview")
        
        # Image upload
        uploaded_image = st.file_uploader("Upload image", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_image:
            # Page selection
            selected_pages = self.render_page_selector(uploaded_pdf)
            
            if not selected_pages:
                st.warning("Please select at least one page")
                return
            
            # Image configuration
            col1, col2 = st.columns(2)
            
            with col1:
                # Preview page selector
                preview_page = st.selectbox(
                    "Preview Page:",
                    selected_pages,
                    index=0,
                    format_func=lambda x: f"Page {x}"
                ) - 1
                
                # Image dimensions
                width = st.number_input("Width (0 = original)", min_value=0, value=0)
                height = st.number_input("Height (0 = original)", min_value=0, value=0)
            
            with col2:
                # Show uploaded image
                st.write("**Uploaded Image:**")
                st.image(uploaded_image, caption="Image to add", width=200)
            
            # Position selection with preview
            x_pos, y_pos = self.render_position_selector(uploaded_pdf, preview_page)
            
            # Apply button
            if st.button("Apply Image to Selected Pages", type="primary"):
                with st.spinner("Adding image to selected pages..."):
                    try:
                        result = self.editor.add_image_with_preview(
                            uploaded_pdf, uploaded_image, selected_pages,
                            x_pos, y_pos, 
                            width if width > 0 else None,
                            height if height > 0 else None
                        )
                        st.success(f"✅ Image added to {len(selected_pages)} pages successfully!")
                        st.download_button(
                            label="📥 Download Modified PDF",
                            data=result,
                            file_name=f"image_added_{uploaded_pdf.name}",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Failed to add image: {str(e)}")
    
    def add_watermark_tool_enhanced(self, uploaded_pdf):
        st.subheader("Add Watermark with Interactive Preview")
        
        # Page selection
        selected_pages = self.render_page_selector(uploaded_pdf)
        
        if not selected_pages:
            st.warning("Please select at least one page")
            return
        
        # Watermark configuration
        col1, col2 = st.columns(2)
        
        with col1:
            watermark_text = st.text_input("Watermark Text", "CONFIDENTIAL")
            font_size = st.slider("Font Size", 20, 100, 50)
            opacity = st.slider("Opacity", 0.1, 1.0, 0.3)
        
        with col2:
            rotation = st.slider("Rotation", 0, 360, 45)
            preview_page = st.selectbox(
                "Preview Page:",
                selected_pages,
                index=0,
                format_func=lambda x: f"Page {x}"
            ) - 1
        
        if watermark_text:
            # Live preview
            st.subheader("🔍 Live Preview")
            self.render_before_after_preview(
                uploaded_pdf, 
                preview_page, 
                "watermark", 
                (watermark_text, font_size, rotation)
            )
            
            # Apply button
            if st.button("Apply Watermark to Selected Pages", type="primary"):
                with st.spinner("Adding watermark to selected pages..."):
                    try:
                        result = self.editor.add_watermark_with_preview(
                            uploaded_pdf, watermark_text, selected_pages,
                            opacity, font_size, rotation
                        )
                        st.success(f"✅ Watermark added to {len(selected_pages)} pages successfully!")
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
    
    # ORGANIZATION TOOLS
    def organization_tools(self):
        st.header("📁 PDF Organization Tools")
        
        org_option = st.selectbox(
            "Choose organization option:",
            ["Merge PDFs", "Split PDF", "Rearrange Pages", "Extract Pages", 
             "Rotate Pages", "Compress PDF"]
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
        elif org_option == "Compress PDF":
            self.compress_pdf_tool()
    
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
            
            elif split_method == "By Page Ranges":
                page_ranges = st.text_input(
                    "Enter page ranges (comma-separated):",
                    placeholder="1-3,4-6,7-10"
                )
                
                if st.button("Split PDF") and page_ranges:
                    with st.spinner("Splitting PDF..."):
                        try:
                            result = self.editor.split_pdf(uploaded_pdf, "range", page_ranges)
                            st.success(f"✅ PDF split into {len(result)} files!")
                            
                            for i, file_data in enumerate(result):
                                st.download_button(
                                    label=f"📥 Download {file_data['filename']}",
                                    data=file_data['data'],
                                    file_name=file_data['filename'],
                                    mime="application/pdf",
                                    key=f"range_{i}"
                                )
                        except Exception as e:
                            st.error(f"❌ Failed to split PDF: {str(e)}")
            
            elif split_method == "Equal Parts":
                pages_per_part = st.number_input(
                    "Pages per part:",
                    min_value=1,
                    value=1
                )
                
                if st.button("Split PDF"):
                    with st.spinner("Splitting PDF..."):
                        try:
                            result = self.editor.split_pdf(uploaded_pdf, "equal", str(pages_per_part))
                            st.success(f"✅ PDF split into {len(result)} files!")
                            
                            for i, file_data in enumerate(result):
                                st.download_button(
                                    label=f"📥 Download {file_data['filename']}",
                                    data=file_data['data'],
                                    file_name=file_data['filename'],
                                    mime="application/pdf",
                                    key=f"equal_{i}"
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
    
    def compress_pdf_tool(self):
        st.subheader("Compress PDF")
        
        uploaded_pdf = st.file_uploader("Upload PDF to compress", type=['pdf'])
        
        if uploaded_pdf:
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
    
    # ANNOTATION TOOLS
    def annotation_tools(self):
        st.header("🎨 PDF Annotation Tools")
        
        annotation_type = st.selectbox(
            "Choose annotation type:",
            ["Highlight Text", "Underline Text", "Strikeout Text", "Add Notes", "Add Stamps"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if annotation_type == "Highlight Text":
                self.highlight_tool(uploaded_pdf)
            elif annotation_type == "Underline Text":
                self.underline_tool(uploaded_pdf)
            elif annotation_type == "Strikeout Text":
                self.strikeout_tool(uploaded_pdf)
            elif annotation_type == "Add Notes":
                self.notes_tool(uploaded_pdf)
            elif annotation_type == "Add Stamps":
                self.stamps_tool(uploaded_pdf)
    
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
    
    def underline_tool(self, uploaded_pdf):
        st.subheader("Add Underlines")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            underline_color = st.color_picker("Underline Color", "#FF0000")
        
        with col2:
            x1 = st.number_input("X1 Position", value=100)
            y1 = st.number_input("Y1 Position", value=100)
            x2 = st.number_input("X2 Position", value=200)
            y2 = st.number_input("Y2 Position", value=120)
        
        if st.button("Add Underline"):
            with st.spinner("Adding underline..."):
                try:
                    result = self.editor.add_underline(
                        uploaded_pdf, page_number-1, [x1, y1, x2, y2], underline_color
                    )
                    st.success("✅ Underline added successfully!")
                    st.download_button(
                        label="📥 Download Underlined PDF",
                        data=result,
                        file_name=f"underlined_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add underline: {str(e)}")
    
    def strikeout_tool(self, uploaded_pdf):
        st.subheader("Add Strikeout")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            strikeout_color = st.color_picker("Strikeout Color", "#FF0000")
        
        with col2:
            x1 = st.number_input("X1 Position", value=100)
            y1 = st.number_input("Y1 Position", value=100)
            x2 = st.number_input("X2 Position", value=200)
            y2 = st.number_input("Y2 Position", value=120)
        
        if st.button("Add Strikeout"):
            with st.spinner("Adding strikeout..."):
                try:
                    result = self.editor.add_strikeout(
                        uploaded_pdf, page_number-1, [x1, y1, x2, y2], strikeout_color
                    )
                    st.success("✅ Strikeout added successfully!")
                    st.download_button(
                        label="📥 Download Strikeout PDF",
                        data=result,
                        file_name=f"strikeout_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add strikeout: {str(e)}")
    
    def notes_tool(self, uploaded_pdf):
        st.subheader("Add Sticky Notes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            note_content = st.text_area("Note Content", "Enter your note here...")
        
        with col2:
            x_pos = st.number_input("X Position", value=100)
            y_pos = st.number_input("Y Position", value=100)
            icon_type = st.selectbox("Icon Type", ["Note", "Comment", "Key", "Help"])
        
        if st.button("Add Note") and note_content:
            with st.spinner("Adding note..."):
                try:
                    result = self.editor.add_note(
                        uploaded_pdf, page_number-1, [x_pos, y_pos], note_content, icon_type
                    )
                    st.success("✅ Note added successfully!")
                    st.download_button(
                        label="📥 Download PDF with Note",
                        data=result,
                        file_name=f"noted_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add note: {str(e)}")
    
    def stamps_tool(self, uploaded_pdf):
        st.subheader("Add Stamps")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            stamp_text = st.selectbox("Stamp Text", ["APPROVED", "REJECTED", "CONFIDENTIAL", "DRAFT", "FINAL"])
            stamp_color = st.color_picker("Stamp Color", "#FF0000")
        
        with col2:
            x_pos = st.number_input("X Position", value=100)
            y_pos = st.number_input("Y Position", value=100)
            width = st.number_input("Width", value=100)
            height = st.number_input("Height", value=50)
        
        if st.button("Add Stamp"):
            with st.spinner("Adding stamp..."):
                try:
                    result = self.editor.add_stamp(
                        uploaded_pdf, page_number-1, [x_pos, y_pos, x_pos+width, y_pos+height], 
                        stamp_text, stamp_color
                    )
                    st.success("✅ Stamp added successfully!")
                    st.download_button(
                        label="📥 Download Stamped PDF",
                        data=result,
                        file_name=f"stamped_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add stamp: {str(e)}")
    
    # SECURITY TOOLS
    def security_tools(self):
        st.header("🔒 PDF Security Tools")
        
        security_option = st.selectbox(
            "Choose security option:",
            ["Add Password Protection", "Remove Password", "Digital Signature", "Check Security"]
        )
        
        uploaded_pdf = st.file_uploader("Upload PDF file", type=['pdf'])
        
        if uploaded_pdf:
            if security_option == "Add Password Protection":
                self.add_password_tool(uploaded_pdf)
            elif security_option == "Remove Password":
                self.remove_password_tool(uploaded_pdf)
            elif security_option == "Digital Signature":
                self.digital_signature_tool(uploaded_pdf)
            elif security_option == "Check Security":
                self.check_security_tool(uploaded_pdf)
    
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
    
    def check_security_tool(self, uploaded_pdf):
        st.subheader("Check PDF Security")
        
        password = st.text_input("Password (if protected)", type="password")
        
        if st.button("Check Security"):
            with st.spinner("Checking PDF security..."):
                try:
                    result = self.security.check_pdf_security(uploaded_pdf, password or None)
                    
                    st.success("✅ Security check completed!")
                    
                    # Display security information
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Security Status:**")
                        st.write(f"Encrypted: {'Yes' if result['is_encrypted'] else 'No'}")
                        st.write(f"Needs Password: {'Yes' if result['needs_password'] else 'No'}")
                        st.write(f"Authenticated: {'Yes' if result['is_authenticated'] else 'No'}")
                    
                    with col2:
                        if result['is_authenticated'] and result['permissions']:
                            st.write("**Permissions:**")
                            for perm, allowed in result['permissions'].items():
                                st.write(f"{perm.replace('can_', '').title()}: {'✅' if allowed else '❌'}")
                    
                    if result['is_authenticated'] and result['metadata']:
                        st.write("**Document Information:**")
                        metadata = result['metadata']
                        st.write(f"Pages: {metadata['page_count']}")
                        if metadata['title']:
                            st.write(f"Title: {metadata['title']}")
                        if metadata['author']:
                            st.write(f"Author: {metadata['author']}")
                        if metadata['creator']:
                            st.write(f"Creator: {metadata['creator']}")
                        
                except Exception as e:
                    st.error(f"❌ Failed to check security: {str(e)}")
    
    # OCR TOOLS
    def ocr_tools(self):
        st.header("🔍 OCR Tools")
        st.info("Convert scanned PDFs and images to searchable, editable text")
        
        uploaded_file = st.file_uploader(
            "Upload scanned PDF or image",
            type=['pdf', 'jpg', 'jpeg', 'png', 'tiff']
        )
        
        if uploaded_file:
            # OCR language selection
            ocr_language = st.selectbox(
                "OCR Language",
                ["eng", "fra", "deu", "spa", "ita", "por", "rus", "chi_sim", "jpn", "kor"],
                index=0,
                help="Select the primary language in your document"
            )
            
            if st.button("Extract Text with OCR", type="primary"):
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

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
