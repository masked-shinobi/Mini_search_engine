import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string

# Download necessary NLTK resource
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

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
