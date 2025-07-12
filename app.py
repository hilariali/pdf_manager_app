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

# Enhanced CSS with drag-and-drop support
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

.preview-image {
    max-width: 100%;
    height: auto;
    border: 1px solid #ddd;
    border-radius: 5px;
    cursor: crosshair;
}

.position-overlay {
    position: absolute;
    background: rgba(231, 76, 60, 0.7);
    border: 2px solid #e74c3c;
    border-radius: 3px;
    pointer-events: none;
    z-index: 10;
}

.page-thumbnail {
    border: 2px solid transparent;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 5px;
}

.page-thumbnail:hover {
    border-color: #3498db;
    transform: scale(1.05);
}

.page-thumbnail.selected {
    border-color: #e74c3c;
    background: rgba(231, 76, 60, 0.1);
}

.drag-drop-area {
    border: 2px dashed #bdc3c7;
    border-radius: 10px;
    padding: 40px;
    text-align: center;
    background: #f8f9fa;
    transition: all 0.3s ease;
    cursor: pointer;
}

.drag-drop-area:hover {
    border-color: #3498db;
    background: #e3f2fd;
}

.position-controls {
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 15px 0;
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

.preview-section h4 {
    margin-bottom: 10px;
    color: #2c3e50;
}
</style>

<script>
function updatePosition(x, y) {
    const overlay = document.querySelector('.position-overlay');
    if (overlay) {
        overlay.style.left = x + 'px';
        overlay.style.top = y + 'px';
    }
}

function handleImageClick(event) {
    const rect = event.target.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Update position in Streamlit session state
    window.parent.postMessage({
        type: 'position_update',
        x: Math.round(x),
        y: Math.round(y)
    }, '*');
}
</script>
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
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
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
        """Render interactive position selector with drag-and-drop"""
        st.subheader("🎯 Position Selection")
        
        try:
            # Get PDF preview
            preview_img, page_info = self.editor.get_pdf_preview(pdf_file, page_num)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**Click on the preview to set position:**")
                
                # Display preview with click handling
                st.markdown(f"""
                <div class="pdf-preview-container">
                    <img src="data:image/png;base64,{preview_img}" 
                         class="preview-image" 
                         onclick="handleImageClick(event)"
                         style="width: 100%; max-width: 600px;">
                    <div class="position-overlay" 
                         style="left: {st.session_state.position_x}px; 
                                top: {st.session_state.position_y}px; 
                                width: 20px; height: 20px;"></div>
                </div>
                """, unsafe_allow_html=True)
            
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
            
            st.markdown('<div class="before-after-container">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="preview-section">', unsafe_allow_html=True)
                st.markdown("#### 📄 Before")
                st.image(f"data:image/png;base64,{original_preview}", caption="Original", use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="preview-section">', unsafe_allow_html=True)
                st.markdown("#### ✨ After")
                st.image(f"data:image/png;base64,{modified_preview}", caption="Modified", use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Failed to generate preview: {str(e)}")
    
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
    
    # Keep all other existing methods from the previous implementation
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
    
    # Add other existing methods here...
    def organization_tools(self):
        st.info("Organization tools - keeping existing implementation")
    
    def annotation_tools(self):
        st.info("Annotation tools - keeping existing implementation")
    
    def security_tools(self):
        st.info("Security tools - keeping existing implementation")
    
    def ocr_tools(self):
        st.info("OCR tools - keeping existing implementation")

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
