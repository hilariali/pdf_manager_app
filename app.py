import streamlit as st
import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules using absolute imports
try:
    from config.settings import APP_CONFIG, UI_CONFIG
    from core.session_manager import SessionManager
    from core.ui_components import UIComponents
    import pages.conversion_page as conversion_page
    import pages.editing_page as editing_page
    import pages.organization_page as organization_page
    import pages.annotation_page as annotation_page
    import pages.security_page as security_page
    import pages.ocr_page as ocr_page
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="PDF Manager Pro",
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
        try:
            if tool_category == "🔄 Convert":
                conversion_page.render()
            elif tool_category == "✏️ Edit":
                editing_page.render()
            elif tool_category == "📁 Organize":
                organization_page.render()
            elif tool_category == "🎨 Annotate":
                annotation_page.render()
            elif tool_category == "🔒 Security":
                security_page.render()
            elif tool_category == "🔍 OCR":
                ocr_page.render()
            else:
                st.error("Page not found!")
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
            st.info("Please check that all required files are present and properly configured.")

if __name__ == "__main__":
    app = PDFManagerApp()
    app.main()
