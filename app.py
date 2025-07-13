import streamlit as st
from pathlib import Path
from config.settings import APP_CONFIG
from core.session_manager import SessionManager
from core.ui_components import UIComponents
from pages import (
    conversion_page,
    editing_page,
    organization_page,
    annotation_page,
    security_page,
    ocr_page
)

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG['app_name'],
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

class PDFManagerApp:
    def __init__(self):
        self.session_manager = SessionManager()
        self.ui_components = UIComponents()
        
        # Initialize session state
        self.session_manager.initialize_session()
        
        # Create temp directory
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    def main(self):
        # Load custom CSS
        self.ui_components.load_custom_css()
        
        # Render header
        self.ui_components.render_header()
        
        # Sidebar navigation
        tool_category = self.ui_components.render_sidebar()
        
        # Route to appropriate page
        self.route_to_page(tool_category)
    
    def route_to_page(self, tool_category):
        """Route to the appropriate page based on user selection"""
        page_mapping = {
            "🔄 Convert": conversion_page,
            "✏️ Edit": editing_page,
            "📁 Organize": organization_page,
            "🎨 Annotate": annotation_page,
            "🔒 Security": security_page,
            "🔍 OCR": ocr_page
        }
        
        if tool_category in page_mapping:
            page_mapping[tool_category].render()
        else:
            st.error("Page not found!")

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
