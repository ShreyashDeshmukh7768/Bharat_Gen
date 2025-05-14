import os
import argparse
import fitz  # PyMuPDF
import docx
import re
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentTextExtractor:
    def __init__(self):
        """
        Initialize the document text extractor with DocTR OCR.
        """
        logger.info("Initializing DocumentTextExtractor...")
        self.ocr_model = ocr_predictor(pretrained=True)
        logger.info("DocumentTextExtractor initialized successfully")

    def _clean_text(self, text):
        """Clean and format the extracted text with more sophisticated processing"""
        # Remove unwanted special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,;:!?\'"-]', ' ', text)
        
        # Handle hyphenated words properly
        text = re.sub(r'(?<=\w)-\s+(?=\w)', '', text)  # Join words broken by hyphen+space
        
        # Remove isolated single characters except 'a' and 'I'
        text = re.sub(r'(?<!\w)[^aAI](?!\w)', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Capitalize first letter of each paragraph
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip().capitalize() for p in paragraphs if p.strip()]
        
        return '\n\n'.join(paragraphs)

    def _format_ocr_output(self, ocr_result):
        """Format the OCR output into properly structured text"""
        formatted_text = []
        
        for page in ocr_result.pages:
            page_text = []
            for block in page.blocks:
                block_text = []
                for line in block.lines:
                    # Join words with proper spacing
                    line_text = ' '.join(word.value for word in line.words)
                    block_text.append(line_text)
                # Join lines within a block with space
                page_text.append(' '.join(block_text))
            # Separate blocks with newlines
            formatted_text.append('\n'.join(page_text))
        
        # Join pages with double newlines
        joined_text = '\n\n'.join(formatted_text)
        return self._clean_text(joined_text)

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF using PyMuPDF and DocTR for images"""
        logger.info(f"Extracting text from PDF: {file_path}")
        
        text = ""
        try:
            # First try direct text extraction
            pdf_document = fitz.open(file_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text("text")
                if page_text:
                    text += page_text + "\n\n"
            
            # Clean the extracted text
            text = self._clean_text(text)
            
            # Fall back to OCR if little text was extracted
            if len(text.strip()) < len(pdf_document) * 100:  # Rough heuristic
                logger.info("Limited text extracted directly, falling back to OCR")
                doc = DocumentFile.from_pdf(file_path)
                result = self.ocr_model(doc)
                text = self._format_ocr_output(result)
                
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file with proper formatting"""
        logger.info(f"Extracting text from DOCX: {file_path}")
        
        try:
            doc = docx.Document(file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                para_text = paragraph.text.strip()
                if para_text:
                    paragraphs.append(para_text)
            
            text = '\n\n'.join(paragraphs)
            text = self._clean_text(text)
            logger.info(f"Successfully extracted {len(text)} characters from DOCX")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            return ""

    def extract_text_from_image(self, file_path):
        """Extract text from image using DocTR with proper formatting"""
        logger.info(f"Extracting text from image: {file_path}")
        
        try:
            doc = DocumentFile.from_images(file_path)
            result = self.ocr_model(doc)
            text = self._format_ocr_output(result)
            logger.info(f"Successfully extracted {len(text)} characters from image")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""

    def extract_text(self, file_path):
        """Extract text from various file types with proper formatting"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return self.extract_text_from_image(file_path)
        else:
            logger.warning(f"Unsupported file format: {file_extension}")
            return ""