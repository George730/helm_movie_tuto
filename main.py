from flask import Flask
import os
import random
# import requests
# import ml_code.recommend as ml_model
import src.train_eval.content_based_filtering.content_recommendv2 as ml_model2

app = Flask(__name__)

@app.route("/")
def main():
    return "Hello, World!"

def get_data_filepath(filename):
    data_folder = "../data_files"
    return os.path.join(data_folder, filename)

# def get_user_data_from_kafka(user_id):
#   response = requests.get("http://128.2.204.215:8080/user/"+str(int(user_id)))
#   response_results = response.json()
#   return response_results

@app.route("/recommend/<int:userid>")
def get_recommendation(userid):
    # if ml_model.isNewUser(userid):
    #     user_details = get_user_data_from_kafka(userid)
    #     print(user_details)
    #     age = user_details['age']
    #     gender = user_details['gender']
    #     occp = user_details['occupation']
    #     if not age:
    #         return ml_model2.get_recommendations(userid)
    #     else:
    #         sim_id = ml_model2.user_similarity(age, gender, occp)
    #         return ml_model2.get_recommendations(sim_id)
    # else:
    #     return ml_model2.get_recommendations(userid)
    base_result = [
        'dragonfly+1976',
        'reckless+1995',
        'vessel+of+wrath+1938',
        'blessed+event+1932',
        'chilly+scenes+of+winter+1979',
        'the+misadventures+of+margaret+1998',
        'heavy+weather+1995',
        'the+crush+1967',
        'the+great+kidnapping+1973',
        'vessel+of+wrath+1938',
        'little+dorrit+1987',
        'canned+dreams+2012',
        'canned+dreams+2012',
        'children+in+the+wind+1937',
        'as+i+was+moving+ahead+occasionally+i+saw+brief+glimpses+of+beauty+2000',
        'dilwale+dulhania+le+jayenge+1995',
        'love+torn+in+a+dream+2000',
        'serving+life+2011',
        'deadline+2004',
        'position+among+the+stars+2011'
        ]
    seed = random.uniform(0, 1)
    if seed < 0.2:
        return ",".join(base_result)
    else:
        return ml_model2.get_recommendations(userid)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
