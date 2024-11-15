import easyocr
import cv2
import numpy as np
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import tempfile
from pdf2image import convert_from_path
from spellchecker import SpellChecker  # For spell correction

# Initialize EasyOCR reader for English
reader = easyocr.Reader(['en'])

# Convert PDF to image (in case a PDF is uploaded)
def pdf_to_image(uploaded_file):
    with open("temp_uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    pdf_path = "temp_uploaded_file.pdf"
    pdf_pages = convert_from_path(pdf_path, dpi=300, poppler_path=r'C:/Users/ajith/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin')

    img_list = []
    for i, page in enumerate(pdf_pages):
        image_path = f'page_{i + 1}.jpg'
        page.save(image_path, 'JPEG')
        img_list.append(image_path)

    return img_list

# Apply advanced preprocessing techniques to improve OCR accuracy
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert image to grayscale

    # Apply adaptive thresholding to improve text contrast
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    # Use Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(thresh, (5, 5), 0)

    # Resize the image (scale up for better resolution)
    height, width = blurred.shape
    scaled_img = cv2.resize(blurred, (int(width * 1.5), int(height * 1.5)))

    return scaled_img

# Perform OCR using EasyOCR and apply post-processing techniques
def extract_handwritten_text(img_list):
    text = ''
    
    for img_path in img_list:
        img = cv2.imread(img_path)
        processed_img = preprocess_image(img)
        
        # Use EasyOCR to extract text from the preprocessed image
        results = reader.readtext(processed_img)

        # Collect the OCR results into the text variable
        for result in results:
            text += result[1] + "\n"
    
    # Correct spelling mistakes using SpellChecker
    spell = SpellChecker()
    corrected_text = []

    for word in text.split():
        corrected_word = spell.correction(word)
        if corrected_word:  # Avoid appending None or empty values
            corrected_text.append(corrected_word)

    return ' '.join(corrected_text)

# Save the extracted text as a PDF using ReportLab (Unicode compatible)
def text_to_pdf(text):
    default_folder_path = "C:/Users/ajith/Desktop/senstive/ocr"
    default_folder_path = os.path.normpath(default_folder_path)

    if not os.path.exists(default_folder_path):
        os.makedirs(default_folder_path)

    output_pdf = os.path.join(default_folder_path, "extracted_text.pdf")

    try:
        c = canvas.Canvas(output_pdf, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica", 12)

        y_position = height - 40
        line_height = 14

        for line in text.splitlines():
            if y_position < 40:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 40

            c.drawString(40, y_position, line)
            y_position -= line_height

        c.save()
        st.success(f"PDF saved successfully at {output_pdf}")
    except Exception as e:
        st.error(f"Error saving PDF: {e}")
        print(f"Error: {e}")

# Streamlit UI
st.title("Handwritten Text Extraction and PDF Generator")

# Upload a file (PDF or image)
uploaded_file = st.file_uploader(label="Upload a PDF or Image with Handwritten Text", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file:
    filename = uploaded_file.name
    
    # Check if it's a PDF or image
    if filename.lower().endswith(".pdf"):
        img_list = pdf_to_image(uploaded_file)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpfile:
            tmpfile.write(uploaded_file.getbuffer())  # Write the uploaded file to a temporary file
            img_list = [tmpfile.name]  # Use the temp file's path

    # Extract text from the image or PDF pages
    extracted_text = extract_handwritten_text(img_list)
    
    if extracted_text:
        st.text_area("Extracted Handwritten Text", extracted_text, height=300)
        
        # Button to convert text to PDF
        if st.button("Convert to PDF"):
            text_to_pdf(extracted_text)
    else:
        st.warning("No text was extracted. Please check the quality of the input.")
