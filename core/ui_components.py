import streamlit as st
import base64
from config.settings import APP_CONFIG, UI_CONFIG
from utils.pdf_editor import PDFEditor

class UIComponents:
    def __init__(self):
        self.editor = PDFEditor()
    
    def load_custom_css(self):
        """Load custom CSS styles"""
        css = f"""
        <style>
        .main-header {{
            text-align: center;
            color: {UI_CONFIG['primary_color']};
            font-size: 3rem;
            margin-bottom: 2rem;
        }}
        
        .pdf-preview-container {{
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            background: #f8f9fa;
            position: relative;
        }}
        
        .before-after-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .preview-section {{
            text-align: center;
        }}
        
        .page-thumbnail {{
            border: 2px solid transparent;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 5px;
        }}
        
        .page-thumbnail:hover {{
            border-color: {UI_CONFIG['secondary_color']};
            transform: scale(1.05);
        }}
        
        .page-thumbnail.selected {{
            border-color: {UI_CONFIG['primary_color']};
            background: rgba(231, 76, 60, 0.1);
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def render_header(self):
        """Render application header"""
        st.markdown(f'<h1 class="main-header">📄 {APP_CONFIG["app_name"]}</h1>', unsafe_allow_html=True)
        st.markdown(f"### {APP_CONFIG['app_description']}")
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        st.sidebar.title("🛠️ Tools")
        return st.sidebar.selectbox(
            "Select Category",
            ["🔄 Convert", "✏️ Edit", "📁 Organize", "🎨 Annotate", "🔒 Security", "🔍 OCR"]
        )
    
    def render_file_uploader(self, label, file_types, accept_multiple=False, help_text=None):
        """Render standardized file uploader"""
        return st.file_uploader(
            label,
            type=file_types,
            accept_multiple_files=accept_multiple,
            help=help_text or "Drag and drop your file here"
        )
    
    def render_page_selector(self, pdf_file, session_manager, max_pages=None):
        """Render interactive page selector with thumbnails"""
        st.subheader("📄 Select Pages")
        
        try:
            # Get page previews
            previews = self.editor.get_all_pages_preview(pdf_file, max_pages or APP_CONFIG['max_pages_preview'])
            
            # Page selection options
            selection_mode = st.radio(
                "Page Selection:",
                ["All Pages", "Specific Pages", "Page Range"],
                horizontal=True
            )
            
            if selection_mode == "All Pages":
                selected_pages = list(range(1, len(previews) + 1))
                session_manager.update_selected_pages(selected_pages)
                st.success(f"Selected all {len(previews)} pages")
                
            elif selection_mode == "Specific Pages":
                selected_pages = self._render_thumbnail_selector(previews, session_manager)
                
            elif selection_mode == "Page Range":
                selected_pages = self._render_range_selector(previews, session_manager)
            
            return session_manager.get('selected_pages', [])
            
        except Exception as e:
            st.error(f"Failed to load page previews: {str(e)}")
            return [1]
    
    def _render_thumbnail_selector(self, previews, session_manager):
        """Render thumbnail grid for page selection"""
        st.write("Click on page thumbnails to select/deselect:")
        
        # Create thumbnail grid
        cols = st.columns(5)
        selected_pages = session_manager.get('selected_pages', [])
        
        for i, preview in enumerate(previews):
            with cols[i % 5]:
                page_num = preview['page_num']
                
                # Create clickable thumbnail
                if st.button(
                    f"Page {page_num}",
                    key=f"page_{page_num}",
                    help=f"Click to toggle selection of page {page_num}"
                ):
                    if page_num in selected_pages:
                        selected_pages.remove(page_num)
                    else:
                        selected_pages.append(page_num)
                    session_manager.update_selected_pages(selected_pages)
                
                # Display thumbnail
                st.image(
                    f"data:image/png;base64,{preview['image']}",
                    caption=f"Page {page_num}",
                    width=100
                )
                
                # Show selection status
                if page_num in selected_pages:
                    st.success("✓ Selected")
                else:
                    st.info("Click to select")
        
        st.write(f"Selected pages: {sorted(selected_pages)}")
        return selected_pages
    
    def _render_range_selector(self, previews, session_manager):
        """Render page range selector"""
        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input("Start Page", min_value=1, max_value=len(previews), value=1)
        with col2:
            end_page = st.number_input("End Page", min_value=start_page, max_value=len(previews), value=len(previews))
        
        selected_pages = list(range(start_page, end_page + 1))
        session_manager.update_selected_pages(selected_pages)
        st.info(f"Selected pages {start_page} to {end_page}")
        return selected_pages
    
    def render_position_selector(self, pdf_file, session_manager, page_num=0):
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
                    value=session_manager.get('position_x', 100),
                    key="pos_x"
                )
                
                new_y = st.number_input(
                    "Y Position", 
                    min_value=0, 
                    max_value=int(page_info['height']), 
                    value=session_manager.get('position_y', 100),
                    key="pos_y"
                )
                
                # Update session state
                session_manager.update_position(new_x, new_y)
                
                # Quick position presets
                self._render_position_presets(page_info, session_manager)
                
                # Page info
                st.info(f"Page size: {int(page_info['width'])} × {int(page_info['height'])} pts")
            
            return session_manager.get('position_x'), session_manager.get('position_y')
            
        except Exception as e:
            st.error(f"Failed to load preview: {str(e)}")
            return 100, 100
    
    def _render_position_presets(self, page_info, session_manager):
        """Render quick position preset buttons"""
        st.write("**Quick Positions:**")
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Top Left"):
                session_manager.update_position(50, 50)
                st.rerun()
            
            if st.button("Center"):
                session_manager.update_position(
                    int(page_info['width'] / 2),
                    int(page_info['height'] / 2)
                )
                st.rerun()
        
        with col_b:
            if st.button("Top Right"):
                session_manager.update_position(
                    int(page_info['width'] - 100),
                    50
                )
                st.rerun()
            
            if st.button("Bottom Right"):
                session_manager.update_position(
                    int(page_info['width'] - 100),
                    int(page_info['height'] - 50)
                )
                st.rerun()
    
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
    
    def render_success_download(self, data, filename, label, mime_type="application/pdf"):
        """Render success message with download button"""
        st.success("✅ Operation completed successfully!")
        st.download_button(
            label=label,
            data=data,
            file_name=filename,
            mime=mime_type
        )
