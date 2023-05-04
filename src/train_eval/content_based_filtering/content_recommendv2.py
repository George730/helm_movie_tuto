import pickle
import os
import requests
import sys
sys.path.append('src/train_eval/content_based_filtering')
# import sys
# sys.path.append("/src//train_eval/content_based_filtering/")
from content_based_filteringv2 import ContentFiltering, UserDataLoader
# from src.train_eval.content_based_filtering import content_based_filteringv2

absolute_path = os.path.dirname(__file__)
cr_path = "content_recommend"
print(os.path.join(absolute_path, cr_path, "userloader.pkl"))

with open(os.path.join(absolute_path, cr_path, "userloader.pkl"), "rb") as f:
    user_loader = pickle.load(file=f)

with open(os.path.join(absolute_path, cr_path, "model.pkl"), "rb") as f:
    content_model = pickle.load(file=f)

with open(os.path.join(absolute_path, cr_path, "base_recommend.pkl"), "rb") as f:
    base_recommend = pickle.load(file=f)

def get_user_data_from_kafka(user_id):
  response = requests.get("http://128.2.204.215:8080/user/"+str(int(user_id)))
  response_results = response.json()
  return response_results

global user_recommend
user_recommend = dict()

def get_recommendations(user_id):
    # If user_id in database
    if user_id in user_loader.user_ids:
        if user_id in user_recommend:
            return ",".join(user_recommend[user_id])
        else:
            result = content_model.predict(user_id)
            user_recommend[user_id] = result
            return ",".join(result)
    # if there is no user info
    else:
        user_details = get_user_data_from_kafka(user_id)
        age = user_details['age']
        gender = user_details['gender']
        occp = user_details['occupation']
        if not age:
            return ",".join(base_recommend)
        else:
            sim_id = user_loader.get_user_similarity(age, gender, occp)
            if sim_id in user_recommend:
                return ",".join(user_recommend[sim_id])
            else:
                result = content_model.predict(sim_id)
                user_recommend[sim_id] = result
                return ",".join(result)