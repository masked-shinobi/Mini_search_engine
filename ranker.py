from rank_bm25 import BM25Okapi
from preprocessor import Preprocessor

class Ranker:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.documents = []  # Original documents {filename: content}
        self.filenames = []  # List of filenames
        self.bm25 = None

    def fit(self, documents):
        """
        Fits the BM25 model with preprocessed documents.
        documents should be a dict {filename: content}
        """
        self.filenames = list(documents.keys())
        tokenized_corpus = [
            self.preprocessor.preprocess(documents[fn]) 
            for fn in self.filenames
        ]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query, top_n=5):
        """
        Scores query against documents and returns top N results.
        Returns a list of tuples (filename, score, snippet)
        """
        tokenized_query = self.preprocessor.preprocess(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Combine filename and scores, sort by score descending
        results = []
        for i in range(len(self.filenames)):
            results.append({
                'filename': self.filenames[i],
                'score': round(float(scores[i]), 4)
            })
            
        # Sort results by score
        ranked_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Filter out 0 scores (completely irrelevant)
        ranked_results = [r for r in ranked_results if r['score'] > 0]
        
        return ranked_results[:top_n]
