import streamlit as st

class SessionManager:
    def __init__(self):
        self.default_values = {
            'selected_pages': [],
            'position_x': 100,
            'position_y': 100,
            'current_page': 1,
            'preview_zoom': 1.5,
            'last_operation': None
        }
    
    def initialize_session(self):
        """Initialize session state with default values"""
        for key, value in self.default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def get(self, key, default=None):
        """Get session state value"""
        return st.session_state.get(key, default)
    
    def set(self, key, value):
        """Set session state value"""
        st.session_state[key] = value
    
    def update_position(self, x, y):
        """Update position coordinates"""
        st.session_state.position_x = x
        st.session_state.position_y = y
    
    def update_selected_pages(self, pages):
        """Update selected pages"""
        st.session_state.selected_pages = pages
    
    def reset_session(self):
        """Reset session state to defaults"""
        for key, value in self.default_values.items():
            st.session_state[key] = value
