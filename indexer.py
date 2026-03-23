import os
import json
from preprocessor import Preprocessor

class Indexer:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.preprocessor = Preprocessor()
        self.inverted_index = {}
        self.documents = {} # Stores original filename -> content (or snippet)

    def build_index(self):
        """
        Reads files from the corpus folder and builds an inverted index.
        """
        if not os.path.exists(self.corpus_path):
            print(f"Corpus directory {self.corpus_path} not found.")
            return

        for filename in os.listdir(self.corpus_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.corpus_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[filename] = content
                    
                    # Preprocess content
                    tokens = self.preprocessor.preprocess(content)
                    
                    # Update inverted index
                    for token in tokens:
                        if token not in self.inverted_index:
                            self.inverted_index[token] = []
                        if filename not in self.inverted_index[token]:
                            self.inverted_index[token].append(filename)
        
        print(f"Indexed {len(self.documents)} documents.")

    def get_index(self):
        return self.inverted_index

    def get_documents(self):
        return self.documents

# Example usage
if __name__ == "__main__":
    # Ensure corpus exists for test
    if not os.path.exists('corpus'): os.mkdir('corpus')
    with open('corpus/test.txt', 'w') as f: f.write("Information retrieval is fun.")
    
    idx = Indexer('corpus')
    idx.build_index()
    print("Inverted Index Sample:", list(idx.get_index().items())[:5])
