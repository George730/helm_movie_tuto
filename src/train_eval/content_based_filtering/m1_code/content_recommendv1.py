import pickle
import numpy as np
import os
import requests


absolute_path = os.path.dirname(__file__)
cr_path = "content_recommend"

with open(os.path.join(absolute_path, cr_path, "user_id.pkl"), "rb") as f:
    user_ids = pickle.load(file=f)

with open(os.path.join(absolute_path, cr_path, "contant_recommend.pkl"), "rb") as f:
    content_recommend = pickle.load(file=f)

with open(os.path.join(absolute_path, cr_path, "base_recommend.pkl"), "rb") as f:
    base_recommend = pickle.load(file=f)

with open(os.path.join(absolute_path, cr_path, "user_feats_pkl"), "rb") as f:
    user_feats = pickle.load(file=f)

with open(os.path.join(absolute_path, cr_path, "user_occp_pkl"), "rb") as f:
    occp_list = pickle.load(file=f)

def get_user_data_from_kafka(user_id):
  response = requests.get("http://128.2.204.215:8080/user/"+str(int(user_id)))
  response_results = response.json()
  return response_results

def get_recommendations(user_id):
    # If user_id in database
    if user_id in user_ids:
        return ",".join(content_recommend[user_id])
    # if there is no user info
    else:
        user_details = get_user_data_from_kafka(user_id)
        age = user_details['age']
        gender = user_details['gender']
        occp = user_details['occupation']
        if not age:
            return ",".join(base_recommend)
        else:
            user_id = user_similarity(age, gender, occp)
            return ",".join(content_recommend[user_id])
    

def user_similarity(age, gender, occp):
    feat = []
    feat.append((age - 8.0)/(90.0 - 8.0) * 2)
    if gender.lower == 'm':
        feat.append(0.)
    else:
        feat.append(1.)
    occp_feat = [0.]*len(occp_list)
    try:
        ind = occp_list.index(occp)
        occp_feat[ind] = 1.
        feat.extend(occp_feat)
    except:
        feat.extend(occp_feat)
    euc_sim = np.linalg.norm(np.array(feat) - user_feats, axis=1)
    sim_id = np.argmin(euc_sim)
    return user_ids[sim_id]