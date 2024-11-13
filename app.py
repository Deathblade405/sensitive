# app.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import get_database, COLLECTION_NAME
from vectorize_pdf import vectorize_pdf, extract_text_from_pdf

def store_sensitive_vector(pdf_path):
    vectorizer, tfidf_matrix = vectorize_pdf(pdf_path)
    db = get_database()
    collection = db[COLLECTION_NAME]

    # Store the vector and feature names in MongoDB
    sensitive_content = {
        "features": vectorizer.get_feature_names_out().tolist(),
        "vector": tfidf_matrix.toarray().tolist()
    }
    collection.delete_many({})  # Clear previous sensitive content
    collection.insert_one(sensitive_content)
    print("Sensitive content vector stored in MongoDB.")

def load_sensitive_vector():
    db = get_database()
    collection = db[COLLECTION_NAME]
    sensitive_content = collection.find_one()
    if sensitive_content:
        return np.array(sensitive_content["vector"]), sensitive_content["features"]
    else:
        raise ValueError("No sensitive content found in MongoDB. Please store it first.")

def check_pdf_for_sensitive_content(pdf_path, threshold=0.2):
    # Load sensitive vector
    sensitive_vector, sensitive_features = load_sensitive_vector()

    # Extract and vectorize the text of the new PDF
    text = extract_text_from_pdf(pdf_path)
    vectorizer, tfidf_matrix = vectorize_pdf(pdf_path)

    # Create a new vector for comparison, matching features of the sensitive vector
    matched_vector = np.zeros((1, len(sensitive_features)))
    for i, feature in enumerate(sensitive_features):
        if feature in vectorizer.get_feature_names_out():
            # If feature matches, add to matched vector
            matched_vector[0, i] = tfidf_matrix[0, vectorizer.get_feature_names_out().tolist().index(feature)]

    # Calculate cosine similarity
    similarity = cosine_similarity(sensitive_vector, matched_vector)[0][0]
    print(f"Similarity: {similarity * 100:.2f}%")

    # Check against threshold
    if similarity >= threshold:
        print("Warning: This document contains sensitive content!")
    else:
        print("No sensitive content detected.")

# Example usage
if __name__ == "__main__":
    # Store sensitive PDF
    store_sensitive_vector("data/sensitive_content.pdf")

    # Check another PDF
    check_pdf_for_sensitive_content("data/test_content8.pdf", threshold=0.2)
