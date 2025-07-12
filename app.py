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
    
    def merge_pdfs_tool(self):
        st.subheader("Merge Multiple PDFs")
        
        uploaded_files = st.file_uploader(
            "Upload PDF files to merge",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if len(uploaded_files) > 1:
            st.info(f"Selected {len(uploaded_files)} files for merging")
            
            # Show file order with drag-and-drop simulation
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
                            
                            # Create download buttons for each split file
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
                rotation_angle = st.selectbox(
                    "Rotation angle:",
                    [90, 180, 270, -90]
                )
            
            with col2:
                page_selection = st.selectbox(
                    "Pages to rotate:",
                    ["All pages", "Specific pages"]
                )
            
            if page_selection == "Specific pages":
                page_numbers = st.text_input(
                    "Enter page numbers (comma-separated):",
                    placeholder="1,3,5"
                )
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
    
    def shapes_tool(self, uploaded_pdf):
        st.subheader("Add Shapes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            page_number = st.number_input("Page Number", min_value=1, value=1)
            shape_type = st.selectbox("Shape Type", ["rectangle", "circle", "line"])
            shape_color = st.color_picker("Shape Color", "#000000")
            fill_color = st.color_picker("Fill Color (optional)", "#FFFFFF")
        
        with col2:
            if shape_type == "rectangle":
                x1 = st.number_input("X1", value=100)
                y1 = st.number_input("Y1", value=100)
                x2 = st.number_input("X2", value=200)
                y2 = st.number_input("Y2", value=150)
                coords = [x1, y1, x2, y2]
            elif shape_type == "circle":
                x = st.number_input("Center X", value=150)
                y = st.number_input("Center Y", value=150)
                radius = st.number_input("Radius", value=50)
                coords = [x, y, radius]
            elif shape_type == "line":
                x1 = st.number_input("Start X", value=100)
                y1 = st.number_input("Start Y", value=100)
                x2 = st.number_input("End X", value=200)
                y2 = st.number_input("End Y", value=200)
                coords = [[x1, y1], [x2, y2]]
        
        if st.button("Add Shape"):
            with st.spinner("Adding shape..."):
                try:
                    result = self.editor.add_shape(
                        uploaded_pdf, page_number-1, shape_type, coords, 
                        shape_color, fill_color if fill_color != "#FFFFFF" else None
                    )
                    st.success("✅ Shape added successfully!")
                    st.download_button(
                        label="📥 Download PDF with Shape",
                        data=result,
                        file_name=f"shape_{uploaded_pdf.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add shape: {str(e)}")
    
    # Add other existing methods here (conversion_tools, editing_tools, etc.)
    # ... (keeping the existing methods from the previous implementation)

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
