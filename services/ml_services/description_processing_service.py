from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import numpy as np
import pickle
import os
import time

def get_board_game_descriptions(db_con):
    with db_con.cursor() as curs:
        curs.execute("""
        SELECT description
        FROM dim_board_games dbg
        ORDER BY id;
    """)
    descriptions = curs.fetchall()
    descriptions = [i[0] for i in descriptions]
    return descriptions


def create_tfidf_vectorizer(descriptions):
    vectorizer = TfidfVectorizer(stop_words='english', max_df=.95, min_df=.05)
    tfidf_vectorizer = vectorizer.fit(descriptions)
    return tfidf_vectorizer

def dump_model(model, pathname):
    pickle.dump(model, open(pathname, "wb"))

def load_model(pathname):
    vectorizer = pickle.load(open(pathname, "rb"))
    return vectorizer

def create_truncate_svd_model(game_data_matrix):
    svd = TruncatedSVD(n_components=100, n_iter=7) # Using 84 components in order to get 95% of the variance
    X_sparse = csr_matrix(game_data_matrix)
    svd_model = svd.fit(X_sparse)
    return svd_model

def create_game_metadata_matrix(db_con):
    pass

def train_model(descriptions, game_metadata_matrix):
        tfidf_vectorizer = create_tfidf_vectorizer(descriptions)
        game_metadata_matrix = np.hstack((X.todense(),game_metadata_matrix))
        svd_model = create_truncate_svd_model(game_metadata_matrix)

        datep = time.strftime("%d_%b_%Y").lower() 
        tfidf_vectorizer_path = os.path.join('models', 'tfidf', datep, 'tfidf_model.pk')
        dump_model(tfidf_vectorizer, tfidf_vectorizer_path)
        
        svd_path = os.path.join('models', 'svd', datep, 'svd_model.pk')
        dump_model(svd_model, svd_path)
        return tfidf_vectorizer, svd_model

def transform_game_data(descriptions, game_metadata_matrix, train_new_model = True):
    if train_new_model:
        tfidf_vectorizer, svd_model = train_model(descriptions, game_metadata_matrix)
    else:
        pass




def get_board_game_names(db_con):
    with db_con.cursor() as curs:
        curs.execute("""
        SELECT name
        FROM dim_board_games dbg
        ORDER BY id;
    """)
    game_names = curs.fetchall()
    game_names = [i[0] for i in game_names]
    return game_names