import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui_components import UIComponents
from utils.pdf_editor import PDFEditor
from utils.pdf_security import PDFSecurity

def render():
    """Render the organization tools page"""
    ui_components = UIComponents()
    editor = PDFEditor()
    security = PDFSecurity()
    
    st.header("📁 PDF Organization Tools")
    
    org_option = st.selectbox(
        "Choose organization option:",
        ["Merge PDFs", "Split PDF", "Rearrange Pages", "Extract Pages", 
         "Rotate Pages", "Compress PDF"]
    )
    
    if org_option == "Merge PDFs":
        _render_merge_tool(ui_components, editor)
    elif org_option == "Split PDF":
        _render_split_tool(ui_components, editor)
    elif org_option == "Rearrange Pages":
        _render_rearrange_tool(ui_components, editor)
    elif org_option == "Extract Pages":
        _render_extract_tool(ui_components, editor)
    elif org_option == "Rotate Pages":
        _render_rotate_tool(ui_components, editor)
    elif org_option == "Compress PDF":
        _render_compress_tool(ui_components, security)

def _render_merge_tool(ui_components, editor):
    """Render merge PDFs tool"""
    st.subheader("Merge Multiple PDFs")
    
    uploaded_files = ui_components.render_file_uploader(
        "Upload PDF files to merge",
        ['pdf'],
        accept_multiple=True
    )
    
    if len(uploaded_files) > 1:
        st.info(f"Selected {len(uploaded_files)} files for merging")
        
        st.write("**Merge Order:**")
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"{i}. {file.name}")
        
        if st.button("Merge PDFs", type="primary"):
            with st.spinner("Merging PDFs..."):
                try:
                    result = editor.merge_pdfs(uploaded_files)
                    ui_components.render_success_download(
                        result,
                        "merged_document.pdf",
                        "📥 Download Merged PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to merge PDFs: {str(e)}")
    else:
        st.warning("Please upload at least 2 PDF files to merge")

def _render_split_tool(ui_components, editor):
    """Render split PDF tool"""
    st.subheader("Split PDF")
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF to split", ['pdf'])
    
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
                        result = editor.split_pdf(uploaded_pdf, "pages", page_numbers)
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
                        result = editor.split_pdf(uploaded_pdf, "range", page_ranges)
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
                        result = editor.split_pdf(uploaded_pdf, "equal", str(pages_per_part))
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

def _render_rearrange_tool(ui_components, editor):
    """Render rearrange pages tool"""
    st.subheader("Rearrange Pages")
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF to rearrange", ['pdf'])
    
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
                    result = editor.rearrange_pages(uploaded_pdf, order_list)
                    ui_components.render_success_download(
                        result,
                        f"rearranged_{uploaded_pdf.name}",
                        "📥 Download Rearranged PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to rearrange pages: {str(e)}")

def _render_extract_tool(ui_components, editor):
    """Render extract pages tool"""
    st.subheader("Extract Pages")
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF to extract pages from", ['pdf'])
    
    if uploaded_pdf:
        page_numbers = st.text_input(
            "Enter page numbers to extract (comma-separated):",
            placeholder="1,3,5,7"
        )
        
        if st.button("Extract Pages") and page_numbers:
            with st.spinner("Extracting pages..."):
                try:
                    pages_list = [int(p.strip()) for p in page_numbers.split(',')]
                    result = editor.extract_pages(uploaded_pdf, pages_list)
                    ui_components.render_success_download(
                        result,
                        f"extracted_{uploaded_pdf.name}",
                        "📥 Download Extracted Pages"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to extract pages: {str(e)}")

def _render_rotate_tool(ui_components, editor):
    """Render rotate pages tool"""
    st.subheader("Rotate Pages")
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF to rotate", ['pdf'])
    
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
                    result = editor.rotate_pages(uploaded_pdf, rotation_angle, pages_list)
                    ui_components.render_success_download(
                        result,
                        f"rotated_{uploaded_pdf.name}",
                        "📥 Download Rotated PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to rotate pages: {str(e)}")

def _render_compress_tool(ui_components, security):
    """Render compress PDF tool"""
    st.subheader("Compress PDF")
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF to compress", ['pdf'])
    
    if uploaded_pdf:
        compression_level = st.selectbox(
            "Compression Level",
            ["low", "medium", "high", "maximum"]
        )
        
        if st.button("Compress PDF"):
            with st.spinner("Compressing PDF..."):
                try:
                    result = security.compress_pdf(uploaded_pdf, compression_level)
                    st.success("✅ PDF compressed successfully!")
                    
                    # Show compression statistics
                    info = result['compression_info']
                    st.info(f"Original size: {info['original_size']:,} bytes")
                    st.info(f"Compressed size: {info['compressed_size']:,} bytes")
                    st.info(f"Compression ratio: {info['compression_ratio']}%")
                    
                    ui_components.render_success_download(
                        result['data'],
                        result['filename'],
                        "📥 Download Compressed PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to compress PDF: {str(e)}")
