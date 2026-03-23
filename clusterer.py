from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from preprocessor import Preprocessor
import pandas as pd

class Clusterer:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.preprocessor = Preprocessor()
        self.vectorizer = TfidfVectorizer(
            tokenizer=self.preprocessor.preprocess,
            token_pattern=None # Suppress warning as we use custom tokenizer
        )

    def cluster_documents(self, documents):
        """
        Clusters a list of document strings into K groups.
        Returns a mapping of cluster_id -> list of filenames.
        """
        filenames = list(documents.keys())
        contents = list(documents.values())
        
        # Generate TF-IDF vectors
        X = self.vectorizer.fit_transform(contents)
        
        # Adjust n_clusters if we have very few documents
        actual_clusters = min(self.n_clusters, len(filenames))
        if actual_clusters < 1: actual_clusters = 1
        
        # Perform K-Means clustering
        kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init='auto')
        kmeans.fit(X)
        
        # Map filenames to their cluster labels
        clusters = {}
        for i, label in enumerate(kmeans.labels_):
            if label not in clusters:
                clusters[int(label)] = []
            clusters[int(label)].append(filenames[i])
            
        return clusters

# Example usage
if __name__ == "__main__":
    docs = {
        "doc1.txt": "AI and machine learning are great.",
        "doc2.txt": "Artificial intelligence is a branch of computer science.",
        "doc3.txt": "Databases store structured information efficiently.",
        "doc4.txt": "Networking protocols like TCP/IP are essential."
    }
    clst = Clusterer(n_clusters=2)
    print("Clusters:", clst.cluster_documents(docs))
