import streamlit as st
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from utils.pdf_editor import PDFEditor

def render():
    """Render the editing tools page"""
    session_manager = SessionManager()
    ui_components = UIComponents()
    editor = PDFEditor()
    
    st.header("✏️ PDF Editing Tools with Interactive Preview")
    
    edit_option = st.selectbox(
        "Choose editing option:",
        ["Add Text", "Add Images", "Add Watermark", "Add Page Numbers"]
    )
    
    uploaded_pdf = ui_components.render_file_uploader(
        "Upload PDF file", 
        ['pdf']
    )
    
    if uploaded_pdf:
        if edit_option == "Add Text":
            _render_add_text_tool(uploaded_pdf, session_manager, ui_components, editor)
        elif edit_option == "Add Images":
            _render_add_image_tool(uploaded_pdf, session_manager, ui_components, editor)
        elif edit_option == "Add Watermark":
            _render_add_watermark_tool(uploaded_pdf, session_manager, ui_components, editor)
        elif edit_option == "Add Page Numbers":
            _render_add_page_numbers_tool(uploaded_pdf, ui_components, editor)

def _render_add_text_tool(uploaded_pdf, session_manager, ui_components, editor):
    """Render add text tool with preview"""
    st.subheader("Add Text to PDF with Interactive Preview")
    
    # Page selection
    selected_pages = ui_components.render_page_selector(uploaded_pdf, session_manager)
    
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
        x_pos, y_pos = ui_components.render_position_selector(uploaded_pdf, session_manager, preview_page)
        
        # Live preview
        st.subheader("🔍 Live Preview")
        ui_components.render_before_after_preview(
            uploaded_pdf, 
            preview_page, 
            "text", 
            (text_content, x_pos, y_pos, font_size, text_color)
        )
        
        # Apply button
        if st.button("Apply Text to Selected Pages", type="primary"):
            with st.spinner("Adding text to selected pages..."):
                try:
                    result = editor.add_text_with_preview(
                        uploaded_pdf, text_content, selected_pages,
                        x_pos, y_pos, font_size, text_color
                    )
                    ui_components.render_success_download(
                        result,
                        f"text_added_{uploaded_pdf.name}",
                        "📥 Download Modified PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add text: {str(e)}")

def _render_add_image_tool(uploaded_pdf, session_manager, ui_components, editor):
    """Render add image tool with preview"""
    st.subheader("Add Image to PDF with Interactive Preview")
    
    # Image upload
    uploaded_image = ui_components.render_file_uploader(
        "Upload image", 
        ['jpg', 'jpeg', 'png']
    )
    
    if uploaded_image:
        # Page selection
        selected_pages = ui_components.render_page_selector(uploaded_pdf, session_manager)
        
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
        x_pos, y_pos = ui_components.render_position_selector(uploaded_pdf, session_manager, preview_page)
        
        # Apply button
        if st.button("Apply Image to Selected Pages", type="primary"):
            with st.spinner("Adding image to selected pages..."):
                try:
                    result = editor.add_image_with_preview(
                        uploaded_pdf, uploaded_image, selected_pages,
                        x_pos, y_pos, 
                        width if width > 0 else None,
                        height if height > 0 else None
                    )
                    ui_components.render_success_download(
                        result,
                        f"image_added_{uploaded_pdf.name}",
                        "📥 Download Modified PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add image: {str(e)}")

def _render_add_watermark_tool(uploaded_pdf, session_manager, ui_components, editor):
    """Render add watermark tool with preview"""
    st.subheader("Add Watermark with Interactive Preview")
    
    # Page selection
    selected_pages = ui_components.render_page_selector(uploaded_pdf, session_manager)
    
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
        ui_components.render_before_after_preview(
            uploaded_pdf, 
            preview_page, 
            "watermark", 
            (watermark_text, font_size, rotation)
        )
        
        # Apply button
        if st.button("Apply Watermark to Selected Pages", type="primary"):
            with st.spinner("Adding watermark to selected pages..."):
                try:
                    result = editor.add_watermark_with_preview(
                        uploaded_pdf, watermark_text, selected_pages,
                        opacity, font_size, rotation
                    )
                    ui_components.render_success_download(
                        result,
                        f"watermarked_{uploaded_pdf.name}",
                        "📥 Download Watermarked PDF"
                    )
                except Exception as e:
                    st.error(f"❌ Failed to add watermark: {str(e)}")

def _render_add_page_numbers_tool(uploaded_pdf, ui_components, editor):
    """Render add page numbers tool"""
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
                result = editor.add_page_numbers(
                    uploaded_pdf, position, font_size, start_number
                )
                ui_components.render_success_download(
                    result,
                    f"numbered_{uploaded_pdf.name}",
                    "📥 Download Numbered PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add page numbers: {str(e)}")
