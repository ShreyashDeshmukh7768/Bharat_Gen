import os
import fitz  # PyMuPDF
import docx
import logging
import openai
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentTextExtractor:
    def __init__(self):
        """
        Initialize the document text extractor with OpenAI API.
        """
        logger.info("Initializing DocumentTextExtractor...")
        # Get API key from environment variable
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        logger.info("DocumentTextExtractor initialized successfully")

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF using OpenAI's API"""
        logger.info(f"Extracting text from PDF: {file_path}")
        
        try:
            # First try direct text extraction as backup
            pdf_document = fitz.open(file_path)
            direct_text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text("text")
                if page_text:
                    direct_text += page_text + "\n\n"
            
            # Use OpenAI for extraction
            # Convert PDF to base64 for API
            with open(file_path, "rb") as pdf_file:
                base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            
            # Call the OpenAI API with the PDF content
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all the text from this PDF document. Maintain the formatting and structure as much as possible."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:application/pdf;base64,{base64_pdf}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            extracted_text = response.choices[0].message.content
            
            # If OpenAI extraction is too short, fall back to direct extraction
            if len(extracted_text.strip()) < 100 and len(direct_text.strip()) > len(extracted_text.strip()):
                logger.info("OpenAI extraction was limited, using direct extraction instead")
                extracted_text = direct_text
                
            logger.info(f"Successfully extracted {len(extracted_text)} characters from PDF")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF with OpenAI: {e}")
            # Return direct text if available as fallback
            if 'direct_text' in locals() and direct_text:
                logger.info("Using direct extraction as fallback")
                return direct_text
            return ""

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        logger.info(f"Extracting text from DOCX: {file_path}")
        
        try:
            # First try direct extraction as backup
            doc = docx.Document(file_path)
            paragraphs = []
            for paragraph in doc.paragraphs:
                para_text = paragraph.text.strip()
                if para_text:
                    paragraphs.append(para_text)
            
            direct_text = '\n\n'.join(paragraphs)
            
            # Convert DOCX to base64
            with open(file_path, "rb") as docx_file:
                base64_docx = base64.b64encode(docx_file.read()).decode('utf-8')
            
            # Call OpenAI API with the DOCX content
            # Note: As OpenAI doesn't directly support DOCX, we'll use a different approach
            # We'll first convert our extracted text and ask ChatGPT to clean and format it
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in extracting and formatting text from documents."
                    },
                    {
                        "role": "user",
                        "content": f"This is the extracted text from a DOCX file. Please clean and format it properly, maintaining paragraph structure:\n\n{direct_text}"
                    }
                ],
                max_tokens=4096
            )
            
            extracted_text = response.choices[0].message.content
            
            # If OpenAI result is too short, fall back to direct extraction
            if len(extracted_text.strip()) < 100 and len(direct_text.strip()) > len(extracted_text.strip()):
                logger.info("OpenAI processing was limited, using direct extraction instead")
                extracted_text = direct_text
                
            logger.info(f"Successfully extracted {len(extracted_text)} characters from DOCX")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX with OpenAI: {e}")
            # Return direct text if available as fallback
            if 'direct_text' in locals() and direct_text:
                logger.info("Using direct extraction as fallback")
                return direct_text
            return ""

    def extract_text_from_image(self, file_path):
        """Extract text from image using OpenAI"""
        logger.info(f"Extracting text from image: {file_path}")
        
        try:
            # Convert image to base64
            with open(file_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Call OpenAI API with the image
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all the text from this image. Maintain the formatting and structure as much as possible."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096
            )
            
            extracted_text = response.choices[0].message.content
            logger.info(f"Successfully extracted {len(extracted_text)} characters from image")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image with OpenAI: {e}")
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