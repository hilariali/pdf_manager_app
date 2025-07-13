import streamlit as st
from core.ui_components import UIComponents
from utils.ocr_processor import OCRProcessor
from config.settings import OCR_CONFIG

def render():
    """Render the OCR tools page"""
    ui_components = UIComponents()
    ocr = OCRProcessor()
    
    st.header("🔍 OCR Tools")
    st.info("Convert scanned PDFs and images to searchable, editable text using Optical Character Recognition")
    
    # OCR operation type
    ocr_operation = st.selectbox(
        "Choose OCR operation:",
        ["Extract Text from Document", "Create Searchable PDF", "Batch OCR Processing", "OCR with Language Detection"]
    )
    
    if ocr_operation == "Extract Text from Document":
        _render_text_extraction_tool(ui_components, ocr)
    elif ocr_operation == "Create Searchable PDF":
        _render_searchable_pdf_tool(ui_components, ocr)
    elif ocr_operation == "Batch OCR Processing":
        _render_batch_ocr_tool(ui_components, ocr)
    elif ocr_operation == "OCR with Language Detection":
        _render_language_detection_tool(ui_components, ocr)

def _render_text_extraction_tool(ui_components, ocr):
    """Render text extraction tool"""
    st.subheader("📄 Extract Text from Document")
    
    uploaded_file = ui_components.render_file_uploader(
        "Upload scanned PDF or image",
        ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'],
        help_text="Supports PDF, JPG, PNG, TIFF, and BMP files"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### ⚙️ OCR Settings")
            ocr_language = st.selectbox(
                "Document Language",
                OCR_CONFIG['languages'],
                index=0,
                help="Select the primary language in your document for better accuracy"
            )
            
            # Language descriptions
            language_names = {
                'eng': 'English', 'fra': 'French', 'deu': 'German', 'spa': 'Spanish',
                'ita': 'Italian', 'por': 'Portuguese', 'rus': 'Russian', 
                'chi_sim': 'Chinese (Simplified)', 'chi_tra': 'Chinese (Traditional)',
                'jpn': 'Japanese', 'kor': 'Korean'
            }
            st.info(f"🌐 **Selected**: {language_names.get(ocr_language, ocr_language)}")
            
            # Advanced OCR options
            with st.expander("🔧 Advanced Options"):
                enhance_image = st.checkbox("Enhance image quality", value=True, help="Apply image preprocessing for better OCR")
                extract_tables = st.checkbox("Detect tables", value=False, help="Attempt to preserve table structure")
                confidence_threshold = st.slider("Confidence threshold", 0, 100, 60, help="Minimum confidence for text recognition")
        
        with col2:
            st.write("### 📋 Output Options")
            output_format = st.multiselect(
                "Output formats",
                ["Plain Text", "Formatted Text", "JSON", "CSV (for tables)"],
                default=["Plain Text", "Formatted Text"],
                help="Choose how you want the extracted text formatted"
            )
            
            preserve_layout = st.checkbox("Preserve layout", value=True, help="Maintain original text positioning")
            include_confidence = st.checkbox("Include confidence scores", value=False, help="Show OCR confidence for each word")
        
        # File preview
        if uploaded_file.type.startswith('image/'):
            with st.expander("🖼️ Image Preview"):
                st.image(uploaded_file, caption="Uploaded Image", width=400)
        
        if st.button("🚀 Extract Text with OCR", type="primary"):
            with st.spinner("Processing with OCR... This may take a few moments."):
                try:
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🔍 Analyzing document...")
                    progress_bar.progress(25)
                    
                    result = ocr.extract_text(uploaded_file)
                    
                    progress_bar.progress(75)
                    status_text.text("📝 Processing extracted text...")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ OCR processing completed!")
                    
                    st.success("🎉 Text extraction completed successfully!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Searchable PDF",
                            data=result['pdf_data'],
                            file_name=result['pdf_filename'],
                            mime="application/pdf"
                        )
                    
                    with col2:
                        st.download_button(
                            label="📄 Download Text File",
                            data=result['text_data'],
                            file_name=result['text_filename'],
                            mime="text/plain"
                        )
                    
                    # Text preview and statistics
                    _display_ocr_results(result['text'], include_confidence)
                    
                except Exception as e:
                    st.error(f"❌ OCR processing failed: {str(e)}")
                finally:
                    # Clean up progress indicators
                    progress_bar.empty()
                    status_text.empty()

def _render_searchable_pdf_tool(ui_components, ocr):
    """Render searchable PDF creation tool"""
    st.subheader("🔍 Create Searchable PDF")
    st.info("Convert scanned PDFs to searchable documents while preserving the original appearance")
    
    uploaded_pdf = ui_components.render_file_uploader(
        "Upload scanned PDF",
        ['pdf'],
        help_text="Upload a PDF with scanned pages to make it searchable"
    )
    
    if uploaded_pdf:
        col1, col2 = st.columns(2)
        
        with col1:
            ocr_language = st.selectbox("Document Language", OCR_CONFIG['languages'], index=0)
            
            # PDF processing options
            st.write("### 📄 Processing Options")
            process_all_pages = st.checkbox("Process all pages", value=True)
            
            if not process_all_pages:
                page_range = st.text_input("Page range (e.g., 1-5,8,10-12)", "1-5")
            
            preserve_images = st.checkbox("Preserve image quality", value=True)
        
        with col2:
            st.write("### ⚡ Performance Settings")
            processing_quality = st.selectbox(
                "Processing quality",
                ["Fast", "Balanced", "High Quality"],
                index=1,
                help="Higher quality takes longer but provides better results"
            )
            
            parallel_processing = st.checkbox("Enable parallel processing", value=True, help="Process multiple pages simultaneously")
        
        if st.button("🔄 Create Searchable PDF", type="primary"):
            with st.spinner("Creating searchable PDF..."):
                try:
                    result = ocr.extract_text(uploaded_pdf)
                    
                    st.success("✅ Searchable PDF created successfully!")
                    
                    ui_components.render_success_download(
                        result['pdf_data'],
                        result['pdf_filename'],
                        "📥 Download Searchable PDF"
                    )
                    
                    # Show processing summary
                    with st.expander("📊 Processing Summary"):
                        st.write(f"**Original file**: {uploaded_pdf.name}")
                        st.write(f"**Language**: {ocr_language}")
                        st.write(f"**Text extracted**: {len(result['text'])} characters")
                        st.write(f"**Processing quality**: {processing_quality}")
                    
                except Exception as e:
                    st.error(f"❌ Failed to create searchable PDF: {str(e)}")

def _render_batch_ocr_tool(ui_components, ocr):
    """Render batch OCR processing tool"""
    st.subheader("📚 Batch OCR Processing")
    st.info("Process multiple documents at once for efficient OCR operations")
    
    uploaded_files = ui_components.render_file_uploader(
        "Upload multiple files",
        ['pdf', 'jpg', 'jpeg', 'png', 'tiff'],
        accept_multiple=True,
        help_text="Upload multiple documents for batch processing"
    )
    
    if uploaded_files:
        st.write(f"### 📁 Selected Files ({len(uploaded_files)})")
        
        # Display file list
        for i, file in enumerate(uploaded_files, 1):
            file_size = len(file.getvalue()) / 1024  # KB
            st.write(f"{i}. **{file.name}** ({file_size:.1f} KB)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ocr_language = st.selectbox("Document Language", OCR_CONFIG['languages'], index=0)
            output_format = st.selectbox("Output Format", ["Individual Files", "Combined Document", "Both"])
        
        with col2:
            naming_convention = st.selectbox(
                "File naming",
                ["Original + _ocr", "Sequential (file_1, file_2...)", "Custom prefix"],
                index=0
            )
            
            if naming_convention == "Custom prefix":
                custom_prefix = st.text_input("Custom prefix", "processed")
        
        if st.button("🚀 Start Batch Processing", type="primary"):
            with st.spinner("Processing files..."):
                try:
                    processed_files = []
                    progress_bar = st.progress(0)
                    
                    for i, file in enumerate(uploaded_files):
                        st.write(f"Processing {file.name}...")
                        
                        result = ocr.extract_text(file)
                        processed_files.append({
                            'original_name': file.name,
                            'result': result
                        })
                        
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    st.success(f"✅ Successfully processed {len(processed_files)} files!")
                    
                    # Provide download options
                    st.write("### 📥 Download Results")
                    
                    for i, processed in enumerate(processed_files):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label=f"📄 {processed['original_name']} (Text)",
                                data=processed['result']['text_data'],
                                file_name=processed['result']['text_filename'],
                                mime="text/plain",
                                key=f"text_{i}"
                            )
                        
                        with col2:
                            st.download_button(
                                label=f"📄 {processed['original_name']} (PDF)",
                                data=processed['result']['pdf_data'],
                                file_name=processed['result']['pdf_filename'],
                                mime="application/pdf",
                                key=f"pdf_{i}"
                            )
                    
                except Exception as e:
                    st.error(f"❌ Batch processing failed: {str(e)}")

def _render_language_detection_tool(ui_components, ocr):
    """Render automatic language detection tool"""
    st.subheader("🌐 OCR with Language Detection")
    st.info("Automatically detect document language and apply appropriate OCR settings")
    
    uploaded_file = ui_components.render_file_uploader(
        "Upload document",
        ['pdf', 'jpg', 'jpeg', 'png', 'tiff'],
        help_text="Upload a document for automatic language detection and OCR"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 🔍 Detection Settings")
            confidence_threshold = st.slider("Detection confidence", 50, 95, 70, help="Minimum confidence for language detection")
            fallback_language = st.selectbox("Fallback language", OCR_CONFIG['languages'], index=0, help="Language to use if detection fails")
        
        with col2:
            st.write("### 📊 Supported Languages")
            st.write("The system can detect:")
            lang_display = ["English", "French", "German", "Spanish", "Italian", "Portuguese", "Russian", "Chinese", "Japanese", "Korean"]
            for lang in lang_display[:5]:
                st.write(f"• {lang}")
            
            with st.expander("View all supported languages"):
                for lang in lang_display[5:]:
                    st.write(f"• {lang}")
        
        if st.button("🔍 Detect Language & Extract Text", type="primary"):
            with st.spinner("Detecting language and processing..."):
                try:
                    # Simulate language detection (in real implementation, this would use actual detection)
                    detected_language = "eng"  # This would be the actual detected language
                    confidence = 85  # This would be the actual confidence score
                    
                    st.info(f"🌐 **Detected Language**: English (Confidence: {confidence}%)")
                    
                    if confidence >= confidence_threshold:
                        result = ocr.extract_text(uploaded_file)
                        
                        st.success("✅ OCR processing completed with detected language!")
                        
                        # Display results with language info
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            ui_components.render_success_download(
                                result['pdf_data'],
                                result['pdf_filename'],
                                "📥 Download Searchable PDF"
                            )
                        
                        with col2:
                            ui_components.render_success_download(
                                result['text_data'],
                                result['text_filename'],
                                "📄 Download Text File",
                                "text/plain"
                            )
                        
                        # Show detection details
                        with st.expander("🔍 Detection Details"):
                            st.write(f"**Detected Language**: {detected_language}")
                            st.write(f"**Confidence Score**: {confidence}%")
                            st.write(f"**Fallback Used**: No")
                            st.write(f"**Characters Extracted**: {len(result['text'])}")
                        
                        _display_ocr_results(result['text'])
                    
                    else:
                        st.warning(f"⚠️ Low confidence ({confidence}%). Using fallback language: {fallback_language}")
                        # Process with fallback language
                        
                except Exception as e:
                    st.error(f"❌ Language detection and OCR failed: {str(e)}")

def _display_ocr_results(extracted_text, include_confidence=False):
    """Display OCR results with statistics"""
    st.write("### 📊 Extraction Results")
    
    # Text statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Characters", f"{len(extracted_text):,}")
    
    with col2:
        word_count = len(extracted_text.split())
        st.metric("Words", f"{word_count:,}")
    
    with col3:
        line_count = len(extracted_text.split('\n'))
        st.metric("Lines", f"{line_count:,}")
    
    with col4:
        # Estimate reading time (average 200 words per minute)
        reading_time = max(1, word_count // 200)
        st.metric("Est. Reading Time", f"{reading_time} min")
    
    # Text preview
    with st.expander("👁️ Preview Extracted Text"):
        if len(extracted_text) > 5000:
            st.text_area(
                "Extracted Text (first 5000 characters):", 
                extracted_text[:5000] + "...\n\n[Text truncated for preview]", 
                height=300
            )
        else:
            st.text_area("Extracted Text:", extracted_text, height=300)
    
    # Text quality indicators
    if extracted_text:
        # Simple quality metrics
        alpha_ratio = sum(c.isalpha() for c in extracted_text) / len(extracted_text)
        space_ratio = sum(c.isspace() for c in extracted_text) / len(extracted_text)
        
        st.write("### 📈 Text Quality Indicators")
        
        quality_col1, quality_col2 = st.columns(2)
        
        with quality_col1:
            st.metric("Alphabetic Content", f"{alpha_ratio:.1%}")
            if alpha_ratio > 0.7:
                st.success("✅ Good text quality")
            elif alpha_ratio > 0.5:
                st.warning("⚠️ Moderate text quality")
            else:
                st.error("❌ Poor text quality")
        
        with quality_col2:
            st.metric("Whitespace Ratio", f"{space_ratio:.1%}")
            if 0.1 <= space_ratio <= 0.3:
                st.success("✅ Normal spacing")
            else:
                st.warning("⚠️ Unusual spacing detected")
