from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import tqdm
def calc_text_uniq_words(text):
    unique_words = set()
    for word in text.split():
        unique_words.add(word)
    return len(unique_words)


def get_tfidf(x_train, x_val, x_test, max_features=50000):
    word_tfidf = TfidfVectorizer(max_features=max_features, analyzer='word', lowercase=True, ngram_range=(1, 3), token_pattern='[a-zA-Z0-9]')
    char_tfidf = TfidfVectorizer(max_features=max_features, analyzer='char', lowercase=True, ngram_range=(1, 5), token_pattern='[a-zA-Z0-9]')

    train_tfidf_word = word_tfidf.fit_transform(x_train)
    val_tfidf_word = word_tfidf.transform(x_val)
    test_tfidf_word = word_tfidf.transform(x_test)

    train_tfidf_char = char_tfidf.fit_transform(x_train)
    val_tfidf_char = char_tfidf.transform(x_val)
    test_tfidf_char = char_tfidf.transform(x_test)

    train_tfidf = sparse.hstack([train_tfidf_word, train_tfidf_char], dtype='float32')
    val_tfidf = sparse.hstack([val_tfidf_word, val_tfidf_char], dtype='float32')
    test_tfidf = sparse.hstack([test_tfidf_word, test_tfidf_char], dtype='float32')

    return train_tfidf, val_tfidf, test_tfidf, word_tfidf, char_tfidf


def get_most_informative_features(vectorizers, clf, n=20):
    feature_names = []
    for vectorizer in vectorizers:
        feature_names.extend(vectorizer.get_feature_names())
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    return coefs_with_fns[:n], coefs_with_fns[:-(n + 1):-1]


def get_bow(texts, words):
    result = np.zeros((len(texts), len(words)))
    print(np.shape(result))
    for i, text in tqdm(enumerate(texts)):
        for j, word in enumerate(words):
            try:
                if word in text:
                    result[i][j] = 1
            except UnicodeDecodeError:
                pass
    return result


def embed_aggregate(seq, embeds, func=np.sum, normalize=False):
    embed_dim = len(embeds[0])
    embed = np.zeros(embed_dim)
    nozeros = 0
    for value in seq:
        if value == 0:
            continue
        embed = func([embed, embeds[value]], axis=0)
        nozeros += 1
    if normalize:
        embed /= nozeros + 1
    return embed


def similarity(seq1, seq2, embeds, pool='max', func=lambda x1, x2: x1 + x2):
    pooling = {
        'max': {'func': np.max},
        'avg': {'func': np.sum, 'normalize': True},
        'sum': {'func': np.sum, 'normalize': False}
    }
    embed1 = embed_aggregate(seq1, embeds, **pooling[pool])
    embed2 = embed_aggregate(seq2, embeds, **pooling[pool])
    return func(embed1, embed2)
