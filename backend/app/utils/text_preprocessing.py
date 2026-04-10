import spacy
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from typing import List

# Setup NLTK paths and corpora
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Load SpaCy small model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If not found, attempts to use the basic model
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

stop_words = set(stopwords.words('english'))

def clean_text_pipeline(text: str) -> List[str]:
    """
    Full NLP preprocessing pipeline utilizing both NLTK and SpaCy
    1. Lowercase
    2. Tokenize (NLTK)
    3. Remove punctuation & stopwords (NLTK)
    4. Lemmatization (SpaCy)
    """
    if not text:
        return []
        
    # 1. Lowercase
    text = text.lower()
    
    # 2. Tokenize using NLTK
    tokens = word_tokenize(text)
    
    # 3. Remove punctuation and stopwords
    clean_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # 4. Lemmatization using SpaCy
    # We join back to string because standard Spacy processes text better in context
    doc = nlp(" ".join(clean_tokens))
    lemmatized_tokens = [token.lemma_ for token in doc]
    
    return lemmatized_tokens

def get_cleaned_string(text: str) -> str:
    """Returns a cleaned, lemmatized string representation."""
    tokens = clean_text_pipeline(text)
    return " ".join(tokens)
