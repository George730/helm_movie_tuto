from content_based_filteringv2 import UserDataLoader, ContentFiltering
import os
import pandas as pd
import pickle
import argparse


RATING_DATA_FILE = os.path.join("data_files", "10000_rate_with_right_id.csv")
# TMDB_FILE = os.path.join("data_files", "TMDB_SomewhatCleaned.csv")

def train(rate_path):
    '''
    Train on the rate_data corresponding to rate_path.
    '''
    if rate_path:
        rate_data = pd.read_csv(rate_path)
    else:
        rate_data = pd.read_csv(RATING_DATA_FILE)
    train_data = rate_data[['user_id', 'title_year', 'user_rating', 'age', 'gender', 'occupation', 'overview']]

    user_data_loader = UserDataLoader(rate_data)
    user_data_loader.get_user_feats()

    content_model = ContentFiltering()
    # content_model.get_tfidf_matrix(train_data)
    # model.save_tfidf_matrix()

    content_model.train(train_data)
    # model.save_recommendation()
    return user_data_loader, content_model

def validation(model, val_path):
    '''
    Validate or test the model.
    '''
    val_data = pd.read_csv(val_path)
    rsme = model.train(val_data, test=True)
    return rsme

def serialize(userloader, model):
    '''
    Serialize the user data loader and the content filtering model.
    '''
    absolute_path = os.path.dirname(__file__)
    cr_path = "content_recommend"
    with open(os.path.join(absolute_path, cr_path, "userloader.pkl"), "wb") as f:
        pickle.dump(userloader, f)
    with open(os.path.join(absolute_path, cr_path, "model.pkl"), "wb") as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description ="Training script.")
    parser.add_argument("ratePath", help="The path to rate data")
    args = parser.parse_args()
    user_data_loader, content_model = train(args.ratePath)
    serialize(user_data_loader, content_model)


    


