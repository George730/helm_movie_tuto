import pandas as pd
import os
import numpy as np
import scipy.linalg as la
import time

from scipy.sparse import coo_matrix, save_npz

data_folder = "data_files"

# combined data file
filename = "10000_rate_with_right_id.csv"

df = pd.read_csv(os.path.join(data_folder, filename), lineterminator='\n')

movies = df[["movie_id", "title", "kafka_id"]].drop_duplicates().sort_values(by="movie_id").reset_index(drop=True)

users = df[["user_id"]].drop_duplicates().sort_values(by="user_id").reset_index(drop=True).reset_index(names="user_idx")


def matrix_data(ratings):
    """
    Represent the user-movie ratings data in a matrix format

    args:
        ratings (pd.DataFrame)  : raw ratings data represented in a pandas DataFrame

    return :
        Tuple[X, user_means, movie_means]
            X (np.array[num_users, num_movies]) : the actual ratings matrix
            user_means (np.array[num_users, ])  : mean user rating array over the observed ratings
            movie_means (np.array[num_movies, ])  : mean movie rating array over the obsevered ratings
    """
    # construct wide table from long format for user-movie rating
    X = ratings.pivot_table(index="user_id", columns="movie_id", values="user_rating")

    # replace NaN for unknown ratings, user avg and movie avg with 0
    X.fillna(0, inplace=True)

    return X.astype("int64").values


def low_rank_matrix_factorization(X_sparse, k, niters=5, lam=10., seed=0):
    """
    Factor a rating matrix into user-features and movie-features.

    args:
        X_sparse (sp.coo_matrix[num_users, num_movies]) : the ratings matrix, assumed sparse in COO format
        k (int) : the number of features in the lower-rank matrices U and V
        niters (int) : number of iterations to run
        lam (float) : regularization parameter, shown as lambda
        seed (int) : the seed for numpy random generator

    return : Tuple(U, V)
        U : np.array[num_users,  k] -- the user-feature matrix
        V : np.array[k, num_movies] -- the movie-feature matrix
    """
    # do not modify this line
    np.random.seed(seed)

    # intialize U and V
    U = np.random.normal(scale=0.1, size=(X_sparse.shape[0], k))
    V = np.random.normal(scale=0.1, size=(k, X_sparse.shape[1]))

    X_row = X_sparse.row
    X_col = X_sparse.col
    for _ in range(niters):
        V_new = []
        for j in range(V.shape[1]):
            # update V with values in U
            condition_ui = np.zeros(X_sparse.shape[0], bool)
            condition_ui[X_row[np.where(X_col == j)[0]]] = True

            # stack row vectors in U at indicies where X_ij is not 0 and
            # perform sum of outer product of rows
            A = np.sum(np.matmul(U[condition_ui, :, np.newaxis], U[condition_ui, np.newaxis, :]), axis=0)

            # calculate conditional sum of u_i*X_ij over
            B = (X_sparse.getcol(j)[condition_ui].T @ U[condition_ui]).reshape((k, 1))
            V_new.append(la.solve(A + lam * np.eye(A.shape[0]), B).reshape((k,)))

        V = np.array(V_new).T

        U_new = []
        for i in range(U.shape[0]):
            # update U with values in V
            condition_vj = np.zeros(X_sparse.shape[1], bool)
            condition_vj[X_col[np.where(X_row == i)[0]]] = True

            # stack column vectors in V at indicies where X_ij is not 0 and
            # perform sum of outer product of transpose of stacked column vectors
            A = np.sum(np.matmul(V[:, condition_vj].T[:, :, np.newaxis], V[:, condition_vj].T[:, np.newaxis, :]),
                       axis=0)

            # calculate conditional sum of v_j*X_ij over
            B = (X_sparse.getrow(i)[:, condition_vj] @ V[:, condition_vj].T).reshape((k, 1))
            U_new.append(la.solve(A + lam * np.eye(A.shape[0]), B).reshape((k,)).T)
        U = np.array(U_new)

    return U, V


def get_prediction_error(X_true, X_pred):
    # binary matrix represent positions where X(i,j) has a known rating
    binary_matrix = np.where(X_true != 0, 1, 0)
    numerator = np.sum(np.multiply(binary_matrix, np.power(X_true - X_pred, 2)))
    denominator = np.sum(binary_matrix)
    return np.sqrt(np.divide(numerator, denominator)).astype(np.float64, copy=False)


X = matrix_data(df[["user_id", "movie_id", "user_rating"]])

train_start_time = time.time()
X_sparse = coo_matrix(X)

k = 25
t = 50
print("Num features:", k)
print("Num Iterations:", t)

U, V = low_rank_matrix_factorization(X_sparse, k, t)
train_end_time = time.time()

print("Training time:", train_end_time - train_start_time, "sec")

X_pred = U @ V
print("RMSE error:", get_prediction_error(X, X_pred))

save_npz(os.path.join(data_folder, "user_movie_sparse.npz"), X_sparse)

np.save(os.path.join(data_folder, "user_matrix.npy"), U)
np.save(os.path.join(data_folder, "movie_matrix.npy"), V)

users.to_csv(os.path.join(data_folder, "user_ids.csv"))
movies.to_csv(os.path.join(data_folder, "movies.csv"))
