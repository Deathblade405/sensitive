# vectorize_pdf.py
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages of a PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip() 

def vectorize_text(text):
    """Vectorizes the given text using TfidfVectorizer."""
    if not text:
        raise ValueError("The extracted text is empty. Cannot vectorize an empty document.")
    
 
    vectorizer = TfidfVectorizer(stop_words=None) 
    tfidf_matrix = vectorizer.fit_transform([text])
    
    return vectorizer, tfidf_matrix

def vectorize_pdf(pdf_path):
    """Extracts text from a PDF and vectorizes it."""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        raise ValueError("The extracted text from the PDF is empty. Cannot proceed with vectorization.")
    return vectorize_text(text)
