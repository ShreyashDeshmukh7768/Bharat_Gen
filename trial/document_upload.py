import streamlit as st
import os
import tempfile
import re
from document_extractor import DocumentTextExtractor
from database import SupabaseClient
from langchain_community.llms import Ollama


class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor with necessary components"""
        self.extractor = DocumentTextExtractor()
        self.db_client = SupabaseClient()
        self.ollama = Ollama(model="phi")

    def extract_medicine_names(self, text):
        """Extract medicine names from text using regex patterns"""
        # Common medicine name patterns
        patterns = [
            r'\b[A-Z][a-z]*(?:mab|nib|zumab|ximab|lizumab|olimab|zomib|tinib|ciclib|rafenib|parin)\b',  # Biological and targeted therapies
            r'\b[A-Z][a-z]*(?:statin|sartan|pril|oxacin|mycin|cycline|cillin|dronate|dipine|febrine|conazole|zosin|vudine|lamide|thiazide|prazole|gliptin)\b',  # Common drug suffixes
            r'\b[A-Z][a-z]*(?:xetine|triptyline|xapine|done|xone|codone|morphone|tadine|navir|vir|vastatin|prazole|pam|lam|tam|zolam|zepam|olol|alol|ipril|pril|one|ine)\b',  # More common drug patterns
            r'\b(?:Aspirin|Tylenol|Advil|Motrin|Aleve|Paracetamol|Ibuprofen|Acetaminophen|Naproxen)\b',  # Common OTC medications
            r'\b\d+\s?(?:mg|mcg|mL|g)\s+[A-Z][a-z]+\b'  # Dosage patterns
        ]
        
        medicines = set()
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                medicines.add(match.group(0))
        
        return list(medicines)

    def generate_summary(self, text):
        """Generate a summary of the document using Ollama Mistral"""
        if len(text) > 12000:  # If text is too long, truncate
            text = text[:12000] + "..."
        
        prompt = f"""Please provide a concise medical summary of the following document. 
Extract key medical information including:
- Medical conditions mentioned
- Treatments discussed
- Key diagnoses
- Notable test results
- Important patient instructions

Text: {text}

Summary (keep it under 500 words):"""

        try:
            summary = self.ollama(prompt)
            return summary
        except Exception as e:
            st.error(f"Error generating summary: {e}")
            return "Failed to generate summary. Please try again."

    def process_document(self, uploaded_file, user_id):
        """Process the uploaded document and save results to database"""
        try:
            # Save the uploaded file to a temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                file_path = tmp_file.name
            
            # Extract text from the document
            extracted_text = self.extractor.extract_text(file_path)
            
            # Extract medicine names
            medicines = self.extract_medicine_names(extracted_text)
            
            # Generate summary
            summary = self.generate_summary(extracted_text)
            
            # Save to database
            result = self.db_client.save_document(
                user_id=user_id,
                file_name=uploaded_file.name,
                extracted_text=extracted_text[:100000],  # Limit text length for DB
                summary=summary,
                medicines=medicines
            )
            
            # Clean up temp file
            os.unlink(file_path)
            
            return result, summary, medicines
            
        except Exception as e:
            st.error(f"Error processing document: {e}")
            return False, "Processing failed", []


def display_document_upload():
    """Display the document upload interface"""
    st.title("Document Upload & Analysis")
    
    # Help text
    st.markdown("""
    Upload medical documents (prescriptions, lab reports, etc.) for automatic analysis. 
    The system will extract text, identify medications, and generate a summary.
    
    **Supported formats:** PDF, DOCX, JPG, PNG, TIFF
    """)
    
    # Upload widget
    uploaded_file = st.file_uploader("Upload a medical document", 
                                     type=["pdf", "docx", "jpg", "jpeg", "png", "tiff", "tif"])
    
    if uploaded_file is not None:
        # Show file info
        st.info(f"File uploaded: {uploaded_file.name}")
        
        # Process button
        if st.button("Process Document", use_container_width=True):
            with st.spinner("Processing document... This may take a minute."):
                processor = DocumentProcessor()
                success, summary, medicines = processor.process_document(uploaded_file, st.session_state['user_id'])
                
                if success:
                    st.success("Document processed successfully!")
                    
                    # Display summary
                    st.subheader("Document Summary")
                    st.write(summary)
                    
                    # Display medicines if any were found
                    if medicines:
                        st.subheader("Medications Identified")
                        for medicine in medicines:
                            st.markdown(f"- {medicine}")
                    else:
                        st.info("No medications were identified in this document.")
                else:
                    st.error("Failed to process document. Please try again.")

    # Display existing documents
    st.markdown("---")
    st.subheader("Your Document History")
    
    db_client = SupabaseClient()
    documents = db_client.get_user_documents(st.session_state['user_id'])
    
    if not documents:
        st.info("You haven't uploaded any documents yet.")
    else:
        for doc in documents:
            with st.expander(f"{doc['file_name']} - {doc['created_at'].split('T')[0]}"):
                st.subheader("Summary")
                st.write(doc['summary'])
                
                if doc['medicines']:
                    st.subheader("Medications")
                    for medicine in doc['medicines']:
                        st.markdown(f"- {medicine}")
                else:
                    st.info("No medications identified in this document.")
                
                # Option to view full text
                if st.button("View Full Text", key=f"view_{doc['id']}", use_container_width=True):
                    st.text_area("Extracted Text", value=doc['extracted_text'], height=300)
                
                # Option to delete
                if st.button("Delete Document", key=f"delete_{doc['id']}", use_container_width=True):
                    if db_client.delete_document(doc['id']):
                        st.success("Document deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete document.")