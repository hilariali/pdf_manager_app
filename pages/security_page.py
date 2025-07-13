import streamlit as st
from core.ui_components import UIComponents
from utils.pdf_security import PDFSecurity
from config.settings import SECURITY_CONFIG

def render():
    """Render the security tools page"""
    ui_components = UIComponents()
    security = PDFSecurity()
    
    st.header("🔒 PDF Security Tools")
    
    security_option = st.selectbox(
        "Choose security option:",
        ["Add Password Protection", "Remove Password", "Digital Signature", 
         "Check Security", "Compress PDF", "Generate File Hash"]
    )
    
    uploaded_pdf = ui_components.render_file_uploader("Upload PDF file", ['pdf'])
    
    if uploaded_pdf:
        if security_option == "Add Password Protection":
            _render_add_password_tool(uploaded_pdf, ui_components, security)
        elif security_option == "Remove Password":
            _render_remove_password_tool(uploaded_pdf, ui_components, security)
        elif security_option == "Digital Signature":
            _render_digital_signature_tool(uploaded_pdf, ui_components, security)
        elif security_option == "Check Security":
            _render_check_security_tool(uploaded_pdf, ui_components, security)
        elif security_option == "Compress PDF":
            _render_compress_tool(uploaded_pdf, ui_components, security)
        elif security_option == "Generate File Hash":
            _render_hash_tool(uploaded_pdf, ui_components, security)

def _render_add_password_tool(uploaded_pdf, ui_components, security):
    """Render password protection tool"""
    st.subheader("Add Password Protection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Password Settings:**")
        user_password = st.text_input("User Password", type="password", help="Password to open the document")
        owner_password = st.text_input("Owner Password (optional)", type="password", help="Password for full access")
        
        if not owner_password:
            st.info("💡 If no owner password is set, user password will be used for both")
    
    with col2:
        st.write("**Security Settings:**")
        encryption_method = st.selectbox(
            "Encryption Method", 
            SECURITY_CONFIG['encryption_methods'],
            index=0,
            help="AES_256 is recommended for maximum security"
        )
        
        st.write("**Document Permissions:**")
        permissions = []
        for perm in SECURITY_CONFIG['permissions']:
            if st.checkbox(perm.replace('_', ' ').title(), value=perm in ['print', 'copy']):
                permissions.append(perm)
    
    # Security level indicator
    if encryption_method == "AES_256":
        st.success("🔒 **High Security**: AES-256 encryption selected")
    elif encryption_method == "AES_128":
        st.info("🔐 **Medium Security**: AES-128 encryption selected")
    else:
        st.warning("⚠️ **Basic Security**: RC4 encryption selected")
    
    if st.button("Add Password Protection", type="primary") and user_password:
        with st.spinner("Adding password protection..."):
            try:
                result = security.add_password(
                    uploaded_pdf, user_password, owner_password or None,
                    encryption_method, permissions
                )
                st.success("✅ Password protection added successfully!")
                
                # Show protection details
                with st.expander("🔍 Protection Details"):
                    st.write(f"**Encryption**: {encryption_method}")
                    st.write(f"**Permissions**: {', '.join(permissions)}")
                    st.write(f"**Protected on**: {result['encryption_info']['protected_date']}")
                
                ui_components.render_success_download(
                    result['data'],
                    result['filename'],
                    "📥 Download Protected PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add password protection: {str(e)}")

def _render_remove_password_tool(uploaded_pdf, ui_components, security):
    """Render password removal tool"""
    st.subheader("Remove Password Protection")
    
    st.info("🔓 **Note**: You need the correct password to remove protection from a PDF")
    
    password = st.text_input("Enter PDF Password", type="password")
    
    # Check if PDF is actually protected
    try:
        security_info = security.check_pdf_security(uploaded_pdf)
        if not security_info['is_encrypted']:
            st.warning("⚠️ This PDF is not password protected")
            return
        else:
            st.info(f"🔒 PDF is encrypted and {'requires' if security_info['needs_password'] else 'does not require'} a password")
    except:
        pass
    
    if st.button("Remove Password", type="primary") and password:
        with st.spinner("Removing password..."):
            try:
                result = security.remove_password(uploaded_pdf, password)
                ui_components.render_success_download(
                    result['data'],
                    result['filename'],
                    "📥 Download Unlocked PDF"
                )
                st.info("🔓 Password protection has been removed from the PDF")
            except Exception as e:
                st.error(f"❌ Failed to remove password: {str(e)}")

def _render_digital_signature_tool(uploaded_pdf, ui_components, security):
    """Render digital signature tool"""
    st.subheader("Add Digital Signature")
    
    st.info("✍️ **Note**: This creates a visual signature. For legal digital signatures, use specialized tools.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        signature_text = st.text_input("Signature Text", "Digitally Signed", help="Text to display in the signature")
        page_number = st.number_input("Page Number", min_value=1, value=1)
        
        # Signature style options
        signature_style = st.selectbox("Signature Style", ["Simple Text", "Bordered Box", "Timestamp"])
    
    with col2:
        st.write("**Signature Position:**")
        x_position = st.slider("X Position", 0, 600, 100)
        y_position = st.slider("Y Position", 0, 800, 100)
        
        # Preview signature area
        st.write("**Preview Area:**")
        st.code(f"Position: ({x_position}, {y_position})\nText: {signature_text}")
    
    if st.button("Add Digital Signature", type="primary"):
        with st.spinner("Adding digital signature..."):
            try:
                result = security.add_digital_signature(
                    uploaded_pdf, signature_text, (x_position, y_position), page_number-1
                )
                
                # Show signature details
                with st.expander("📝 Signature Details"):
                    info = result['signature_info']
                    st.write(f"**Signer**: {info['signer']}")
                    st.write(f"**Timestamp**: {info['timestamp']}")
                    st.write(f"**Page**: {info['page']}")
                
                ui_components.render_success_download(
                    result['data'],
                    result['filename'],
                    "📥 Download Signed PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to add digital signature: {str(e)}")

def _render_check_security_tool(uploaded_pdf, ui_components, security):
    """Render security check tool"""
    st.subheader("Check PDF Security")
    
    password = st.text_input("Password (if protected)", type="password", help="Enter password if the PDF is protected")
    
    if st.button("Check Security", type="primary"):
        with st.spinner("Checking PDF security..."):
            try:
                result = security.check_pdf_security(uploaded_pdf, password or None)
                
                st.success("✅ Security check completed!")
                
                # Display security information in organized sections
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("### 🔒 Security Status")
                    st.write(f"**Encrypted**: {'✅ Yes' if result['is_encrypted'] else '❌ No'}")
                    st.write(f"**Needs Password**: {'✅ Yes' if result['needs_password'] else '❌ No'}")
                    st.write(f"**Authenticated**: {'✅ Yes' if result['is_authenticated'] else '❌ No'}")
                
                with col2:
                    if result['is_authenticated'] and result['permissions']:
                        st.write("### 🛡️ Document Permissions")
                        for perm, allowed in result['permissions'].items():
                            icon = '✅' if allowed else '❌'
                            perm_name = perm.replace('can_', '').replace('_', ' ').title()
                            st.write(f"**{perm_name}**: {icon}")
                
                if result['is_authenticated'] and result['metadata']:
                    st.write("### 📄 Document Information")
                    metadata = result['metadata']
                    
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        st.write(f"**Pages**: {metadata['page_count']}")
                        if metadata['title']:
                            st.write(f"**Title**: {metadata['title']}")
                        if metadata['author']:
                            st.write(f"**Author**: {metadata['author']}")
                    
                    with info_col2:
                        if metadata['creator']:
                            st.write(f"**Creator**: {metadata['creator']}")
                        if metadata['producer']:
                            st.write(f"**Producer**: {metadata['producer']}")
                        if metadata['creation_date']:
                            st.write(f"**Created**: {metadata['creation_date']}")
                        
            except Exception as e:
                st.error(f"❌ Failed to check security: {str(e)}")

def _render_compress_tool(uploaded_pdf, ui_components, security):
    """Render PDF compression tool"""
    st.subheader("Compress PDF")
    
    col1, col2 = st.columns(2)
    
    with col1:
        compression_level = st.selectbox(
            "Compression Level",
            ["low", "medium", "high", "maximum"],
            index=1,
            help="Higher compression reduces file size but may affect quality"
        )
        
        # Compression level descriptions
        descriptions = {
            "low": "Minimal compression, best quality",
            "medium": "Balanced compression and quality",
            "high": "Strong compression, good quality",
            "maximum": "Maximum compression, may reduce quality"
        }
        st.info(f"💡 **{compression_level.title()}**: {descriptions[compression_level]}")
    
    with col2:
        # Show original file size
        original_size = len(uploaded_pdf.getvalue())
        st.metric("Original File Size", f"{original_size:,} bytes")
        
        # Estimated compression ratios
        estimates = {"low": 5, "medium": 15, "high": 30, "maximum": 50}
        estimated_reduction = estimates[compression_level]
        st.info(f"📊 **Estimated reduction**: ~{estimated_reduction}%")
    
    if st.button("Compress PDF", type="primary"):
        with st.spinner("Compressing PDF..."):
            try:
                result = security.compress_pdf(uploaded_pdf, compression_level)
                
                # Show compression statistics
                info = result['compression_info']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Size", f"{info['original_size']:,} bytes")
                with col2:
                    st.metric("Compressed Size", f"{info['compressed_size']:,} bytes")
                with col3:
                    st.metric("Space Saved", f"{info['compression_ratio']}%")
                
                ui_components.render_success_download(
                    result['data'],
                    result['filename'],
                    "📥 Download Compressed PDF"
                )
            except Exception as e:
                st.error(f"❌ Failed to compress PDF: {str(e)}")

def _render_hash_tool(uploaded_pdf, ui_components, security):
    """Render file hash generation tool"""
    st.subheader("Generate File Hash")
    
    st.info("🔐 **File hashing** creates a unique fingerprint for integrity verification")
    
    hash_algorithm = st.selectbox(
        "Hash Algorithm",
        ["sha256", "sha1", "md5", "sha512"],
        index=0,
        help="SHA-256 is recommended for security"
    )
    
    # Algorithm descriptions
    descriptions = {
        "sha256": "Secure Hash Algorithm 256-bit (Recommended)",
        "sha1": "Secure Hash Algorithm 160-bit (Legacy)",
        "md5": "Message Digest 5 (Fast, less secure)",
        "sha512": "Secure Hash Algorithm 512-bit (Most secure)"
    }
    st.write(f"**{hash_algorithm.upper()}**: {descriptions[hash_algorithm]}")
    
    if st.button("Generate Hash", type="primary"):
        with st.spinner("Generating file hash..."):
            try:
                result = security.generate_file_hash(uploaded_pdf, hash_algorithm)
                
                st.success("✅ Hash generated successfully!")
                
                # Display hash information
                st.write("### 🔐 File Hash Information")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Algorithm**: {result['algorithm'].upper()}")
                    st.write(f"**File Size**: {result['file_size']:,} bytes")
                    st.write(f"**Filename**: {result['filename']}")
                
                with col2:
                    st.write("**Hash Value**:")
                    st.code(result['hash'], language="text")
                
                # Copy to clipboard functionality
                st.write("### 📋 Hash Details")
                hash_details = f"""File: {result['filename']}
Algorithm: {result['algorithm'].upper()}
Size: {result['file_size']:,} bytes
Hash: {result['hash']}"""
                
                st.text_area("Hash Information (Copy this)", hash_details, height=100)
                
            except Exception as e:
                st.error(f"❌ Failed to generate hash: {str(e)}")
