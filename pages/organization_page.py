import streamlit as st
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

# Additional helper functions for other organization tools...
def _render_rearrange_tool(ui_components, editor):
    """Render rearrange pages tool"""
    # Implementation similar to split tool
    pass

def _render_extract_tool(ui_components, editor):
    """Render extract pages tool"""
    # Implementation similar to split tool
    pass

def _render_rotate_tool(ui_components, editor):
    """Render rotate pages tool"""
    # Implementation similar to split tool
    pass

def _render_compress_tool(ui_components, security):
    """Render compress PDF tool"""
    # Implementation using security module
    pass
