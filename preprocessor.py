import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string

# Handle NLTK data for serverless environments (Vercel)
import os
import nltk

# Use /tmp as it's the only writable directory on Vercel
nltk_data_path = os.path.join('/tmp', 'nltk_data')
# Ensure the path is recognized by NLTK
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

def setup_nltk():
    try:
        # Check if punkt is already present to skip download
        nltk.data.find('tokenizers/punkt', paths=[nltk_data_path])
    except LookupError:
        if not os.path.exists(nltk_data_path):
            os.makedirs(nltk_data_path)
        # Download essential packs
        for package in ['punkt', 'stopwords', 'punkt_tab']:
            nltk.download(package, download_dir=nltk_data_path, quiet=True)

# We will call this from app.py during initialization
# setup_nltk()

class Preprocessor:
    def __init__(self):
        # Initialize stop words and stemmer
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def preprocess(self, text):
        """
        Performs tokenization, stopword removal, and stemming.
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize (split text into words)
        tokens = word_tokenize(text)
        
        # Filter out stop words and apply stemming
        filtered_tokens = [
            self.stemmer.stem(w) for w in tokens 
            if w not in self.stop_words and w.isalnum()
        ]
        
        return filtered_tokens

# Example usage (if run as a script)
if __name__ == "__main__":
    pp = Preprocessor()
    sample = "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms and systems."
    print(f"Original: {sample}")
    print(f"Preprocessed: {pp.preprocess(sample)}")
