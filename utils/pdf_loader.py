import os
import PyPDF2
from transformers import pipeline

# Initialize the question-answering pipeline
nlp = pipeline("question-answering")

def load_pdfs(directory):
    """Load PDFs and extract their text content."""
    pdf_data = []
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            with open(os.path.join(directory, file), 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() or ''  # Handling None return
                pdf_data.append((file, text)) 
    return pdf_data

def semantic_search_pdfs(query, pdf_data):
    """Perform semantic search on loaded PDFs using the Hugging Face model."""
    answers = []
    for pdf_name, text in pdf_data:

        result = nlp(question=query, context=text)
        answers.append((pdf_name, result['answer']))
    
    if answers:
        return answers
    return "No information found in the PDFs."

