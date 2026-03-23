from flask import Flask, render_template, request, jsonify
from indexer import Indexer
from ranker import Ranker
from clusterer import Clusterer
import os

app = Flask(__name__)

# Initialize components
CORPUS_PATH = 'corpus/'
indexer = Indexer(CORPUS_PATH)
ranker = Ranker()
clusterer = Clusterer(n_clusters=4)

# Initialize index and ranker once at the start
from preprocessor import setup_nltk

def initialize_engine():
    # Setup NLTK (downloads only if missing in /tmp)
    setup_nltk()
    
    if not os.path.exists(CORPUS_PATH):
        os.makedirs(CORPUS_PATH)
        
    indexer.build_index()
    ranker.fit(indexer.get_documents())

# Flag to check if engine is ready
_engine_initialized = False

def ensure_initialized():
    global _engine_initialized
    if not _engine_initialized:
        initialize_engine()
        _engine_initialized = True

@app.route('/')
def index():
    """Search UI"""
    ensure_initialized() # Ensure engine is initialized on first request
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Ranked search results"""
    ensure_initialized()
    query = request.form.get('query')
    if not query:
        return render_template('index.html', error="Please enter a search term.")
    
    # Reload documents if needed (for dynamic corpus updates)
    indexer.build_index()
    ranker.fit(indexer.get_documents())
    
    results = ranker.search(query)
    
    # Trace data for animation
    trace = {
        'query': query,
        'tokens': indexer.preprocessor.preprocess(query),
        'results_count': len(results),
        'top_n_data': results[:5], 
        'inverted_index': {},
        'bm25_stats': {
            'avgdl': round(ranker.bm25.avgdl, 2),
            'k1': 1.5, # Default BM25Okapi k1
            'b': 0.75  # Default BM25Okapi b
        }
    }
    
    # Add document-specific stats for the top results
    for res in trace['top_n_data']:
        # Find index of this doc in ranker
        if res['filename'] in ranker.filenames:
            doc_idx = ranker.filenames.index(res['filename'])
            res['doc_len'] = ranker.bm25.doc_len[doc_idx]
    
    # Fill relevant inverted index hits for trace
    full_index = indexer.get_index()
    for token in trace['tokens']:
        if token in full_index:
            trace['inverted_index'][token] = full_index[token]
    
    # Add snippets to results
    for res in results:
        content = indexer.get_documents().get(res['filename'], "")
        res['snippet'] = content[:200] + "..." if len(content) > 200 else content

    return render_template('results.html', query=query, results=results, trace=trace)

@app.route('/clusters')
def clusters():
    """Document clusters"""
    ensure_initialized()
    docs = indexer.get_documents()
    
    if not docs:
        return render_template('clusters.html', clusters={})
        
    cluster_mapping = clusterer.cluster_documents(docs)
    return render_template('clusters.html', clusters=cluster_mapping)

if __name__ == '__main__':
    app.run(debug=True)
