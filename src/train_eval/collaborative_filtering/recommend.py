from scipy.sparse import load_npz
from collections import Counter
import numpy as np
import pandas as pd
import os
#import argparse

def get_data_filepath(filename):
    data_folder = "data_files"
    return os.path.join(data_folder, filename)


X_sparse = load_npz(get_data_filepath("user_movie_sparse.npz"))
U = np.load(get_data_filepath("user_matrix.npy"))
V = np.load(get_data_filepath("movie_matrix.npy"))

users = pd.read_csv(get_data_filepath("user_ids.csv"), index_col="Unnamed: 0")
movies = pd.read_csv(get_data_filepath("movies.csv"), index_col="Unnamed: 0")

# generate user-rating prediction matrix from low-rank matrices
X_pred = U @ V

# using boolean condition to replace existing ratings with 0 in X_pred
X_pred = np.argsort(-np.where((X_sparse != 0).toarray(), 0, X_pred))


def recommend_movies(user_idx=None, size=20):
    """
    Compute user ratings from lower rank matrices. Return required
    number of top-rated movies.

    args:
        user_idx: index of user in the user-movie matrix used in training

    return:
        List[int] -- a list of indices of recommended movies for user
            If new user, send top movie names.
    """
    if user_idx is not None:
        recommendations = X_pred[user_idx, :size][0]
    else:
        # prob: every new user gets same recommendation
        recommendations = X_pred[:, 0]
        counts = Counter(recommendations)
        recommendations = [m_idx for m_idx, _ in counts.most_common(size)]
        recommendations = recommendations[:size]
    return recommendations


def most_recommended_movies(recommended_movie_ids):
    """
    Convert movie indices to movie ids as per training data
    """
    movie_ids = [movies.iloc[m_id].kafka_id for m_id in recommended_movie_ids]
    return ",".join(movie_ids)


def get_recommendations(user_id, size=20):
    """
    Client side method to get movie ids in decreasing order of recommendation

    args:
        user_id: (int)

    return:
        movie_ids: (list)
    """
    if isNewUser(user_id):
        user_idx = users[users["user_id"] == user_id]["user_idx"]
        movie_idx = recommend_movies(user_idx, size)
    else:
        # cold start
        movie_idx = recommend_movies(size=size)

    return most_recommended_movies(movie_idx)


def isNewUser(user_id):
    """
    """
    # check if existing user
    user = users[users["user_id"] == user_id]

    if user.shape[0]:
        return False
    return True
