import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re # regex
import string
import contractions
import emoji

def clean_text(text: str, tokenize: bool = False, remove_stop_words: bool = False, stem_words: bool = False, remove_url: bool = False, remove_emojis: str = "convert"):
    """
    #### Description:
    This function is to clean the text from stopwords, punctuation and return a clean text for further analysis

    Args:
        text (str):
            The dataframe containing the text data
        
        tokenize (bool):
            True = return tokenized data
            False = return untokenized data
        
        remove_stop_words (bool):
            True = remove stop words
            False = do not remove stop words

        stem_words (bool):
            True = get the base words (i.e. spraying -> spray)
            False = leave the words as is

        remove_url (bool):
            True = Remove the url in the text
            False = leave the text as is
        
        remove_emojis (str):
            "remove" = Removes the emoji in text
            "convert = converts emoji to text (e.g. ❤️ -> :red_heart:)
            "keep" = keeps the emoji as is
    """

    stemmer = PorterStemmer()
    stop_words = set(stopwords.words("english"))

    def tokenize_text(text):
        return [w for s in sent_tokenize(text) for w in word_tokenize(s)]
    
    def remove_special_characters(text):
        # keep letters, numbers, underscores, colons (for demojized emojis)
        text = re.sub('[^a-zA-Z0-9_]', ' ', text)
        text = re.sub('\s+', ' ', text)
        return text

    def stem_text(tokens):
        return [stemmer.stem(t) for t in tokens]

    def remove_stopwords_func(tokens):
        return [w for w in tokens if w not in stop_words]

    def remove_url_func(text):
        return re.sub(r'https?://\S+|www\.\S+', '', text)

    # Clean process
    text = str(text)

    text = contractions.fix(text)                        # fixing contraction

    text = text.strip().lower()                          # lowercase + trim

    if remove_url:
        text = remove_url_func(text)                     # remove url
    
    # Handle emojis
    if remove_emojis.lower() == "remove":
        text = remove_special_characters(text)  # removes emojis

    elif remove_emojis.lower() == "convert":
        text = emoji.demojize(text, language="en")  # e.g.,  -> ❤️ -> :red_heart:

    elif remove_emojis.lower() == "keep":
        pass

    text = remove_special_characters(text)               # Remove other special characters (but preserve converted emojis with underscores)
    
    tokens = tokenize_text(text)                         # tokenize words

    if remove_stop_words:
        tokens = remove_stopwords_func(tokens)           # remove stopwords
        
    if stem_words:
        tokens = stem_text(tokens)                       # stemming

    if tokenize:
        return tokens                                    # return as tokens
    else:
        return " ".join(tokens)                          # return as string