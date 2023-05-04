from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import numpy as np
import pickle
import os


# class TrainDataLoader:
#     def __init__(self, train_data, tmdb_data):
#         self.train_data = train_data
#         self.tmdb_data = tmdb_data

#     def get_train_data(self):
#         '''
#         get_train_data returns the transformed,
#         non-duplicate training data in dataframe format
#         '''
#         movie_col = list(self.tmdb_data.columns)
#         movie_col.append('title_year')
#         movie_data = self.ratings_data[movie_col]
#         self.train_data = movie_data.drop_duplicates(ignore_index=True)
#         return self.train_data
    
class UserDataLoader:
    def __init__(self, rate_data):
        user_col = ['age', 'gender', 'occupation']
        self.user_feat = rate_data[user_col].drop_duplicates(ignore_index=True)
        self.user_feat.fillna(-1, inplace=True)

        self.user_ids = rate_data['user_id'].unique().tolist()

        self.min_ = self.user_feat['age'].min()
        self.max_ = self.user_feat['age'].max()

        self.occp_list = list(self.user_feat['occupation'].unique())
        # remove nan
        del self.occp_list[-1]

    
    def occp(self, x):
        '''
        occp func get an occupation and returns a one-hot representation, 
        unless it is a new occupation, then returns zeros.
        '''
        try:
            i = np.eye(len(self.occp_list))
            ind = self.occp_list.index(x)
            return list(i[ind])
        except:
            return list(np.zeros(len(self.occp_list)))
    
    def minmax(self, x):
        '''
        minmax func normalize the age into [0,1],
        returns a list of a singe age score.
        '''
        return [(x - self.min_)/(self.max_ - self.min_)]

    def gender(self, x):
        '''
        gender maps male to [0] and female to [1], 
        if the gender is not given, ot returns [-1].
        '''
        if pd.isna(x) or x == -1:
            return [-1.]
        elif x.lower() == 'm':
            return [0.]
        elif x.lower() == 'f':
            return [1.]
        else:
            return [-1.]
        
    def get_user_feats(self):
        '''
        concat all the features for users,
        return the numpy array of shape (num_users, num_occp + 2).
        '''
        self.user_feat['occupation'] = self.user_feat['occupation'].apply(self.occp)
        self.user_feat['age'] = self.user_feat['age'].apply(self.minmax)
        self.user_feat['gender'] = self.user_feat['gender'].apply(self.gender)

        user_feats = self.user_feat['age'] + self.user_feat['gender'] + self.user_feat['occupation']
        user_feats = pd.DataFrame(user_feats, columns=['list'])
        user_feats = np.stack(user_feats.list)
        self.user_feats = user_feats
        # return user_feats
    
    def get_user_similarity(self, age, gender, occp):
        '''
        get_user_sim returns the most similar user in the database,
        given age, gender and occupation based on Euclidean distance
        '''
        if self.user_feats is None:
            raise RuntimeError("Get user_feats before training: call UserDataLoader.get_user_feats")
        
        feat = []
        feat.extend(self.minmax(age))
        feat.extend(self.gender(gender))
        feat.extend(self.occp(occp))
        euc_sim = np.linalg.norm(np.array(feat) - self.user_feats, axis=1)
        sim_id = np.argmin(euc_sim)
        return self.user_ids[sim_id]
    
    def get_user_similarity_m(self, test_user_feats):
        '''
        get_user_sim_m returns the most similar user in the database,
        given a matrix containing new_user_feats based on Euclidean distance
        '''
        if self.user_feats is None:
            raise RuntimeError("Get user_feats before training: call UserDataLoader.get_user_feats")
        
        euc_sim = np.linalg.norm(test_user_feats[:, np.newaxis, :] - self.user_feats, axis=2)
        sim_id = np.argmin(euc_sim, 1)
        return self.user_ids[sim_id]
    
    def save(self):
        absolute_path = os.path.dirname(__file__)
        cr_path = "content_recommend"
        with open(os.path.join(absolute_path, cr_path, "userloader.pkl"), "wb") as fp:
            pickle.dump(self, fp, protocol=pickle.HIGHEST_PROTOCOL)
    
class ContentFiltering:
    def __init__(self, analyzer="word", ngram_range= (1, 2), min_df=1, stop_words="english", max_features=1000000):
        self.tfidf_vectorizer = TfidfVectorizer(
            analyzer=analyzer, ngram_range=ngram_range,
            min_df=min_df, stop_words=stop_words, max_features=max_features)

        # Needs to be set explicitly
        # self.movie_ids = None

    def get_tfidf_matrix(self, train_data, test=False):
        '''
        returns the tfidf matrix based on train_data
        '''
        if self.tfidf_vectorizer is None:
            raise RuntimeError("ContentFiltering is not initialized.")
        if test:
            return self.tfidf_vectorizer.transform(train_data['overview'])
        else:
            train_data_overview = train_data[["title_year_overview", "title_year"]].drop_duplicates(subset=['title_year'], ignore_index=True)
            return self.tfidf_vectorizer.fit_transform(train_data_overview["title_year_overview"].astype('U').values)

    def get_idx_id_map(self, data):
        '''
        get_idx_id_map returns the mapping between movie id and idx
        vice and versa
        '''
        data = data[["title_year", "overview"]].drop_duplicates(subset=['title_year'], ignore_index=True)
        movie_idx_id = dict([(k, v) for k,v in zip(data.index, data['title_year'])])
        movie_id_idx = dict([(k, v) for k,v in zip(data['title_year'], data.index)])
        return movie_idx_id, movie_id_idx

    def get_true_feat(self, train_data, user_id, movie_id_idx, tfidf_matrix):
        '''
        get_true_feat returns the preference vector of a given user,
        sum(rate_norm * movie_feat for all (movie_feat, rate_norm) of a user).
        '''
        movie_id_rate = train_data[train_data['user_id'] == user_id][['title_year', 'user_rating']]
        feat = []
        for x, y in zip(movie_id_rate['title_year'], movie_id_rate['user_rating']):
            # rate_norm definition
            rate_norm = (y-3.0)/2.0
            movie_idx = movie_id_idx[x]
            # movie_feat definition
            feat.append(tfidf_matrix[movie_idx] * rate_norm)
        return sum(feat)

    def train(self, train_data, test=False):
        '''
        get the recommendation lists for all train users.
        '''
        # if self.tfidf_matrix is None:
        #     raise RuntimeError("Get tfidf_matrix before training: call ContentFiltering.get_tfidf_matrix")
        #
        self.content_recommendation = dict()
        train_data['title_year_overview'] = train_data["title_year"] + " " + train_data["overview"]
        train_data['title_year_overview'] = train_data['title_year_overview'].str.replace('+', ' ')
        self.train_data = train_data
        movie_idx_id, movie_id_idx = self.get_idx_id_map(train_data)
        self.movie_idx_id, self.movie_id_idx = movie_idx_id, movie_id_idx
        # print("get idx map done")
        tfidf_matrix = self.get_tfidf_matrix(train_data, test)
        self.tfidf_matrix = tfidf_matrix
        # print("get tfidf done")
        # user_ids = train_data['user_id'].unique().tolist()

        # if test:
        #     mses, nnzs = [], []

        # print("training...")
        # for user_id in user_ids:
        #     true_feat = self.get_true_feat(train_data, user_id, movie_id_idx, tfidf_matrix)
        #     cos1 = linear_kernel(tfidf_matrix, true_feat)
        #     sim_scores = list(enumerate(cos1))
        #     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        #     if test:
        #         pred_feat = tfidf_matrix[sim_scores[1][0]]
        #         diff = true_feat - pred_feat
        #         mse = diff.power(2).sum()
        #         mses.append(mse)
        #         nnzs.append(diff.nnz)
        #     else:
        #         # TODO: remove all movies the user has rated
        #         sim_scores = sim_scores[1:21]
        #         movie_ids = [movie_idx_id[i[0]] for i in sim_scores]
        #         self.content_recommendation[user_id] = movie_ids
        
        # if test:
        #     return np.sqrt(sum(mses)/sum(nnzs))
        # print("Done")
    
    def save(self):
        absolute_path = os.path.dirname(__file__)
        cr_path = "content_recommend"
        with open(os.path.join(absolute_path, cr_path, "model.pkl"), "wb") as fp:
            pickle.dump(self, fp, protocol=pickle.HIGHEST_PROTOCOL)
        
    def predict(self, user_id):
        true_feat = self.get_true_feat(self.train_data, user_id, self.movie_id_idx, self.tfidf_matrix)
        cos1 = linear_kernel(self.tfidf_matrix, true_feat)
        sim_scores = list(enumerate(cos1))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        movie_ids = [self.movie_idx_id[i[0]] for i in sim_scores[1:21]]
        # return self.content_recommendation[user_id]
        return movie_ids



