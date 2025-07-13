import streamlit as st
from core.ui_components import UIComponents
from utils.pdf_editor import PDFEditor

def render():
    """Render the annotation tools page"""
    ui_components = UIComponents()
    editor = PDFEditor()
    
    st.header("🎨 PDF Annotation Tools")
    
    annotation_type = st.selectbox(
        "Choose annotation type:",
        ["Highlight Text", "Underline Text", "Strikeout Text", "Squiggly Underline",
         "Add Notes", "Add Text Box", "Add Stamps", "Add Shapes"]
    )
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF file", ['pdf'])
    
    if uploaded_pdf:
        if annotation_type == "Highlight Text":
            _render_highlight_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Underline Text":
            _render_underline_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Strikeout Text":
            _render_strikeout_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Squiggly Underline":
            _render_squiggly_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Add Notes":
            _render_notes_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Add Text Box":
            _render_text_box_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Add Stamps":
            _render_stamps_tool(uploaded_pdf, ui_components, editor)
        elif annotation_type == "Add Shapes":
            _render_shapes_tool(uploaded_pdf, ui_components, editor)

def _render_highlight_tool(uploaded_pdf, ui_components, editor):
    """Render highlight annotation tool"""
    st.subheader("Add Highlights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        highlight_color = st.color_picker("Highlight Color", "#FFFF00")
        
        st.info("💡 **Tip**: Select the area you want to highlight by setting coordinates")
    
    with col2:
        st.write("**Highlight Area Coordinates:**")
        x1 = st.number_input("X1 Position (Left)", value=100)
        y1 = st.number_input("Y1 Position (Top)", value=100)
        x2 = st.number_input("X2 Position (Right)", value=200)
        y2 = st.number_input("Y2 Position (Bottom)", value=120)
    
    # Preview section
    with st.expander("📄 Preview Page"):
        try:
            preview_img, page_info = editor.get_pdf_preview(uploaded_pdf, page_number-1)
            st.image(f"data:image/png;base64,{preview_img}", caption=f"Page {page_number}", width=600)
            st.info(f"Page size: {int(page_info['width'])} × {int(page_info['height'])} pts")
        except Exception as e:
            st.error(f"Failed to load preview: {str(e)}")
    
    if st.button("Add Highlight", type="primary"):
        with st.spinner("Adding highlight..."):
            try:
                result = editor.add_highlight(
                    uploaded_pdf, page_number-1, [x1, y1, x2, y2], highlight_color
                )
                ui_components.render_success_download(
                    result,
                    f"highlighted_{uploaded_pdf.name}",
                    "📥 Download Highlighted PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add highlight: {str(e)}")

def _render_underline_tool(uploaded_pdf, ui_components, editor):
    """Render underline annotation tool"""
    st.subheader("Add Underlines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        underline_color = st.color_picker("Underline Color", "#FF0000")
    
    with col2:
        st.write("**Underline Area Coordinates:**")
        x1 = st.number_input("X1 Position", value=100)
        y1 = st.number_input("Y1 Position", value=100)
        x2 = st.number_input("X2 Position", value=200)
        y2 = st.number_input("Y2 Position", value=120)
    
    if st.button("Add Underline", type="primary"):
        with st.spinner("Adding underline..."):
            try:
                result = editor.add_underline(
                    uploaded_pdf, page_number-1, [x1, y1, x2, y2], underline_color
                )
                ui_components.render_success_download(
                    result,
                    f"underlined_{uploaded_pdf.name}",
                    "📥 Download Underlined PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add underline: {str(e)}")

def _render_strikeout_tool(uploaded_pdf, ui_components, editor):
    """Render strikeout annotation tool"""
    st.subheader("Add Strikeout")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        strikeout_color = st.color_picker("Strikeout Color", "#FF0000")
    
    with col2:
        st.write("**Strikeout Area Coordinates:**")
        x1 = st.number_input("X1 Position", value=100)
        y1 = st.number_input("Y1 Position", value=100)
        x2 = st.number_input("X2 Position", value=200)
        y2 = st.number_input("Y2 Position", value=120)
    
    if st.button("Add Strikeout", type="primary"):
        with st.spinner("Adding strikeout..."):
            try:
                result = editor.add_strikeout(
                    uploaded_pdf, page_number-1, [x1, y1, x2, y2], strikeout_color
                )
                ui_components.render_success_download(
                    result,
                    f"strikeout_{uploaded_pdf.name}",
                    "📥 Download Strikeout PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add strikeout: {str(e)}")

def _render_squiggly_tool(uploaded_pdf, ui_components, editor):
    """Render squiggly underline annotation tool"""
    st.subheader("Add Squiggly Underline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        squiggly_color = st.color_picker("Squiggly Color", "#00FF00")
    
    with col2:
        st.write("**Squiggly Area Coordinates:**")
        x1 = st.number_input("X1 Position", value=100)
        y1 = st.number_input("Y1 Position", value=100)
        x2 = st.number_input("X2 Position", value=200)
        y2 = st.number_input("Y2 Position", value=120)
    
    if st.button("Add Squiggly Underline", type="primary"):
        with st.spinner("Adding squiggly underline..."):
            try:
                result = editor.add_squiggly(
                    uploaded_pdf, page_number-1, [x1, y1, x2, y2], squiggly_color
                )
                ui_components.render_success_download(
                    result,
                    f"squiggly_{uploaded_pdf.name}",
                    "📥 Download Squiggly PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add squiggly underline: {str(e)}")

def _render_notes_tool(uploaded_pdf, ui_components, editor):
    """Render sticky notes tool"""
    st.subheader("Add Sticky Notes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        note_content = st.text_area("Note Content", "Enter your note here...", height=100)
        icon_type = st.selectbox("Icon Type", ["Note", "Comment", "Key", "Help", "NewParagraph", "Paragraph"])
    
    with col2:
        st.write("**Note Position:**")
        x_pos = st.number_input("X Position", value=100)
        y_pos = st.number_input("Y Position", value=100)
        
        st.info("💡 **Tip**: Click on the PDF preview to place your note at the desired location")
    
    if st.button("Add Note", type="primary") and note_content.strip():
        with st.spinner("Adding note..."):
            try:
                result = editor.add_note(
                    uploaded_pdf, page_number-1, [x_pos, y_pos], note_content, icon_type
                )
                ui_components.render_success_download(
                    result,
                    f"noted_{uploaded_pdf.name}",
                    "📥 Download PDF with Note"
                )
            except Exception as e:
                st.error(f"❌ Failed to add note: {str(e)}")

def _render_text_box_tool(uploaded_pdf, ui_components, editor):
    """Render text box annotation tool"""
    st.subheader("Add Text Box")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        text_content = st.text_area("Text Content", "Enter your text here...", height=100)
        font_size = st.slider("Font Size", 8, 24, 12)
    
    with col2:
        st.write("**Text Box Area:**")
        x1 = st.number_input("X1 Position (Left)", value=100)
        y1 = st.number_input("Y1 Position (Top)", value=100)
        x2 = st.number_input("X2 Position (Right)", value=300)
        y2 = st.number_input("Y2 Position (Bottom)", value=150)
    
    if st.button("Add Text Box", type="primary") and text_content.strip():
        with st.spinner("Adding text box..."):
            try:
                result = editor.add_text_annotation(
                    uploaded_pdf, page_number-1, [x1, y1, x2, y2], text_content, font_size
                )
                ui_components.render_success_download(
                    result,
                    f"textbox_{uploaded_pdf.name}",
                    "📥 Download PDF with Text Box"
                )
            except Exception as e:
                st.error(f"❌ Failed to add text box: {str(e)}")

def _render_stamps_tool(uploaded_pdf, ui_components, editor):
    """Render stamps tool"""
    st.subheader("Add Stamps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        stamp_text = st.selectbox(
            "Stamp Text", 
            ["APPROVED", "REJECTED", "CONFIDENTIAL", "DRAFT", "FINAL", "REVIEWED", "URGENT", "COPY"]
        )
        custom_stamp = st.text_input("Custom Stamp Text (optional)")
        stamp_color = st.color_picker("Stamp Color", "#FF0000")
    
    with col2:
        st.write("**Stamp Position & Size:**")
        x_pos = st.number_input("X Position", value=100)
        y_pos = st.number_input("Y Position", value=100)
        width = st.number_input("Width", value=100, min_value=50)
        height = st.number_input("Height", value=50, min_value=20)
    
    # Use custom stamp text if provided
    final_stamp_text = custom_stamp if custom_stamp.strip() else stamp_text
    
    if st.button("Add Stamp", type="primary"):
        with st.spinner("Adding stamp..."):
            try:
                result = editor.add_stamp(
                    uploaded_pdf, page_number-1, 
                    [x_pos, y_pos, x_pos+width, y_pos+height], 
                    final_stamp_text, stamp_color
                )
                ui_components.render_success_download(
                    result,
                    f"stamped_{uploaded_pdf.name}",
                    "📥 Download Stamped PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add stamp: {str(e)}")

def _render_shapes_tool(uploaded_pdf, ui_components, editor):
    """Render shapes tool"""
    st.subheader("Add Shapes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        page_number = st.number_input("Page Number", min_value=1, value=1)
        shape_type = st.selectbox("Shape Type", ["rectangle", "circle", "line"])
        shape_color = st.color_picker("Shape Color", "#000000")
        fill_color = st.color_picker("Fill Color (optional)", "#FFFFFF")
        use_fill = st.checkbox("Use fill color")
    
    with col2:
        st.write(f"**{shape_type.title()} Parameters:**")
        
        if shape_type == "rectangle":
            x1 = st.number_input("X1 (Left)", value=100)
            y1 = st.number_input("Y1 (Top)", value=100)
            x2 = st.number_input("X2 (Right)", value=200)
            y2 = st.number_input("Y2 (Bottom)", value=150)
            coords = [x1, y1, x2, y2]
            
        elif shape_type == "circle":
            x = st.number_input("Center X", value=150)
            y = st.number_input("Center Y", value=150)
            radius = st.number_input("Radius", value=50, min_value=1)
            coords = [x, y, radius]
            
        elif shape_type == "line":
            x1 = st.number_input("Start X", value=100)
            y1 = st.number_input("Start Y", value=100)
            x2 = st.number_input("End X", value=200)
            y2 = st.number_input("End Y", value=200)
            coords = [[x1, y1], [x2, y2]]
    
    if st.button("Add Shape", type="primary"):
        with st.spinner("Adding shape..."):
            try:
                result = editor.add_shape(
                    uploaded_pdf, page_number-1, shape_type, coords, 
                    shape_color, fill_color if use_fill else None
                )
                ui_components.render_success_download(
                    result,
                    f"shape_{uploaded_pdf.name}",
                    "📥 Download PDF with Shape"
                )
            except Exception as e:
                st.error(f"❌ Failed to add shape: {str(e)}")
