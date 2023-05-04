import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
import numpy as np
import time
import warnings
warnings.filterwarnings("ignore")

def get_recommendations(user_id, rate_data, movie_id_idx, movie_idx_id, tfidf_matrix):
    movie_id_rate = rate_data[rate_data['user_id'] == user_id][['kafka_id', 'user_rating']]
    feat = []
    for x, y in zip(movie_id_rate['kafka_id'], movie_id_rate['user_rating']):
        rate_norm = (y-3.0)/2.0
        movie_idx = movie_id_idx[x]
        feat.append(tfidf_matrix[movie_idx] * rate_norm)
    feat = sum(feat)
    cos1 = linear_kernel(tfidf_matrix, feat)
    sim_scores = list(enumerate(cos1))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:21]
    movie_ids = [movie_idx_id[i[0]] for i in sim_scores]
    pred_feat = tfidf_matrix[sim_scores[1][0]]
    diff = feat - pred_feat
    return movie_ids, diff, diff.nnz

def get_user_feat(rate_data):
    user_col = ['user_age', 'user_gender', 'user_occupation']
    user_feat = rate_data[user_col]
    user_feat.fillna(-1, inplace=True)
    occp_list = list(user_feat['user_occupation'].unique())
    occp_list.remove(-1)
    with open("content_recommend/user_occp_pkl", "wb") as f:
        pickle.dump(occp_list, f)

    def occp(x):
        try:
            i = np.eye(len(occp_list))
            ind = occp_list.index(x)
            return list(i[ind])
        except:
            return list(np.zeros(len(occp_list)))
    user_feat['user_occupation'] = user_feat['user_occupation'].apply(occp)

    def minmax(x):
        return [(x - 8.0)/(90.0 - 8.0) * 2]
    user_feat['user_age'] = user_feat['user_age'].apply(minmax)

    def gender(x):
        if x == -1:
            return [-1.]
        elif x.lower() == 'm':
            return [0.]
        else:
            return [1.]
    user_feat['user_gender'] = user_feat['user_gender'].apply(gender)

    user_feats = user_feat['user_age'] + user_feat['user_gender'] + user_feat['user_occupation']
    user_feats = pd.DataFrame(user_feats, columns=['list'])
    user_feats = np.stack(user_feats.list)
    return user_feats

if __name__ == '__main__':
    # Read tmdb and user rate data
    print("Start reading data...")
    tmdb_data = pd.read_csv("data_files/TMDB_SomewhatCleaned.csv")
    rate_data = pd.read_csv("data_files/10000_rate_with_right_id.csv")

    # Define movie columns
    movie_col = tmdb_data.columns
    movie_col = list(movie_col)
    movie_col.append('kafka_id')

    # Get movie only data and its non-duplicate
    movie_data = rate_data[movie_col]
    movie_data_nonduplicate = movie_data.drop_duplicates(ignore_index=True)

    # Create two way mapping between index and movie id
    print("Creating mappings...")
    movie_idx_id = dict([(k, v) for k,v in zip(movie_data_nonduplicate.index, movie_data_nonduplicate['kafka_id'])])
    movie_id_idx = dict([(k, v) for k,v in zip(movie_data_nonduplicate['kafka_id'], movie_data_nonduplicate.index)])

    # Train the content filtering model (a matrix of movie features) and save it
    movie_data_nonduplicate['overview'] = movie_data_nonduplicate['overview'].fillna('')
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1, stop_words='english')
    tfidf_matrix = tf.fit_transform(movie_data_nonduplicate['overview'])
    with open("ml_code2/content_recommend/tfidf_matrix.pkl", "wb") as f:
        pickle.dump(tfidf_matrix, f)

    # Make inference on all seen data and save it
    print("Start training...")
    user_ids = list(rate_data['user_id'].unique())
    content_recommendation = dict()
    mses = []
    nnzs = []
    a = time.time()
    for user_id in user_ids:
        movie_ids, diff, nnz = get_recommendations(user_id, rate_data, movie_id_idx, movie_idx_id, tfidf_matrix)
        content_recommendation[user_id] = movie_ids
        mse = diff.power(2).sum()
        mses.append(mse)
        nnzs.append(nnz)
    b = time.time()
    print("Training cost (in seconds):", b-a)
    print("RMSE:", np.sqrt(sum(mses)/sum(nnzs)))


    # save the results for future recommendation
    with open("ml_code2/content_recommend/contant_recommend.pkl", "wb") as f:
        pickle.dump(content_recommendation, f)

    # save user feats
    user_feats = get_user_feat(rate_data)
    with open("ml_code2/content_recommend/user_feats_pkl", "wb") as f:
        pickle.dump(user_feats, f)
