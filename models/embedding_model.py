"""
Embedding Model Module
Uses Sentence-BERT (all-MiniLM-L6-v2) for generating semantic embeddings.
Provides cosine similarity computation between job descriptions and candidate profiles.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Wraps Sentence-Transformers for generating and comparing embeddings.
    Uses the lightweight 'all-MiniLM-L6-v2' model for fast inference.
    """

    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedding model.

        Args:
            model_name: Name of the sentence-transformers model to use.
                       Default is 'all-MiniLM-L6-v2' (80MB, 384 dimensions).
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the sentence-transformers model with error handling."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except ImportError:
            logger.warning("sentence-transformers not available. Using TF-IDF fallback.")
            self.model = None
            self._init_tfidf_fallback()
        except Exception as e:
            logger.warning(f"Failed to load SentenceTransformer: {e}. Using TF-IDF fallback.")
            self.model = None
            self._init_tfidf_fallback()

    def _init_tfidf_fallback(self):
        """Initialize TF-IDF vectorizer as fallback when sentence-transformers is unavailable."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.tfidf_fitted = False
        self.corpus_texts = []

    def encode(self, texts):
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of strings to encode.

        Returns:
            numpy.ndarray of shape (n_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]

        if self.model is not None:
            return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        else:
            return self._tfidf_encode(texts)

    def _tfidf_encode(self, texts):
        """TF-IDF based encoding as fallback."""
        self.corpus_texts.extend(texts)
        all_texts = list(set(self.corpus_texts))
        matrix = self.tfidf.fit_transform(all_texts)
        self.tfidf_fitted = True

        result = []
        for text in texts:
            vec = self.tfidf.transform([text]).toarray()
            result.append(vec[0])
        return np.array(result)

    def compute_similarity(self, text_a, text_b):
        """
        Compute cosine similarity between two texts.

        Args:
            text_a: First text string.
            text_b: Second text string.

        Returns:
            float: Cosine similarity score between 0 and 1.
        """
        emb_a = self.encode(text_a)
        emb_b = self.encode(text_b)
        sim = cosine_similarity(emb_a, emb_b)[0][0]
        return float(sim)

    def compute_similarity_batch(self, job_text, candidate_texts):
        """
        Compute similarity between one job description and multiple candidates.

        Args:
            job_text: Job description text.
            candidate_texts: List of candidate profile texts.

        Returns:
            numpy.ndarray: Array of similarity scores.
        """
        job_emb = self.encode(job_text)
        cand_embs = self.encode(candidate_texts)
        similarities = cosine_similarity(job_emb, cand_embs)[0]
        return similarities

    def encode_documents(self, documents):
        """
        Encode a batch of documents for vector indexing.

        Args:
            documents: List of text documents.

        Returns:
            numpy.ndarray: Matrix of document embeddings.
        """
        return self.encode(documents)

    def get_embedding_dimension(self):
        """Get the dimension of the embedding vectors."""
        if self.model is not None:
            return self.model.get_sentence_embedding_dimension()
        else:
            return len(self.tfidf.vocabulary_) if hasattr(self, 'tfidf') else 384