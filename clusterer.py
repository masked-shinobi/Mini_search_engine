from preprocessor import Preprocessor
import math
import random

class Clusterer:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        self.preprocessor = Preprocessor()

    def _get_tf_idf_vectors(self, documents):
        """Simple manual TF-IDF vectorization"""
        filenames = list(documents.keys())
        contents = [self.preprocessor.preprocess(doc) for doc in documents.values()]
        
        # Build vocabulary
        vocab = sorted(list(set(token for doc_tokens in contents for token in doc_tokens)))
        vocab_idx = {token: i for i, token in enumerate(vocab)}
        
        # Calculate IDF
        df = {token: 0 for token in vocab}
        for doc_tokens in contents:
            for token in set(doc_tokens):
                df[token] += 1
        
        idf = {token: math.log(len(filenames) / (1 + count)) for token, count in df.items()}
        
        # Build vectors
        vectors = []
        for doc_tokens in contents:
            vec = [0.0] * len(vocab)
            tf = {token: doc_tokens.count(token) for token in set(doc_tokens)}
            for token, count in tf.items():
                vec[vocab_idx[token]] = (count / len(doc_tokens)) * idf[token]
            vectors.append(vec)
            
        return vectors, filenames

    def cluster_documents(self, documents):
        """Manual K-Means implementation to save 200MB+ in deployment bundle"""
        if not documents: return {}
        
        vectors, filenames = self._get_tf_idf_vectors(documents)
        if not vectors: return {0: filenames}
        
        num_docs = len(vectors)
        num_features = len(vectors[0])
        n_clusters = min(self.n_clusters, num_docs)
        
        # Initialize centroids randomly
        centroids = random.sample(vectors, n_clusters)
        
        # Iterate (max 10 for speed)
        labels = [0] * num_docs
        for _ in range(10):
            # Assign clusters
            for i in range(num_docs):
                min_dist = float('inf')
                for c_idx, centroid in enumerate(centroids):
                    # Euclidean distance
                    dist = math.sqrt(sum((vectors[i][j] - centroid[j])**2 for j in range(num_features)))
                    if dist < min_dist:
                        min_dist = dist
                        labels[i] = c_idx
            
            # Update centroids
            new_centroids = [[0.0] * num_features for _ in range(n_clusters)]
            counts = [0] * n_clusters
            for i in range(num_docs):
                c_idx = labels[i]
                counts[c_idx] += 1
                for j in range(num_features):
                    new_centroids[c_idx][j] += vectors[i][j]
            
            for c_idx in range(n_clusters):
                if counts[c_idx] > 0:
                    centroids[c_idx] = [val / counts[c_idx] for val in new_centroids[c_idx]]
        
        # Map labels to filenames
        result = {}
        for i, label in enumerate(labels):
            if label not in result: result[label] = []
            result[label].append(filenames[i])
            
        return result

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
