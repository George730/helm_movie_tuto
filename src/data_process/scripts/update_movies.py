import pandas as pd
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import time

start_time = time.time()

old_movie_df = pd.read_csv("../csvs/movie_data.csv")

new_movies = set(line.strip() for line in open('../csvs/movie_update_file.txt'))

old_movies = set(old_movie_df["title_year"])

movies_to_add = new_movies.difference(old_movies)

data_to_append = {}
tmdb_to_title_year = {}

"""# Set up helpers to clean data"""
def convert_to_more_readable(obj):
    l=[]
    try:
      for i in obj:
          l.append(i['name'])
    except:
      pass
    return l

def remove_spaces(obj):
    new_obj = []
    for i in obj:
        new_obj.append(i.replace(" ",""))
    return new_obj

def getcast(obj):
    l=[]
    counter=0
    try:
      for i in obj:
          if counter!=3:
              l.append(i['name'])
              counter+=1
          else:
              break
    except:
      pass
    return l

def getdir(obj):
    l=[]
    try:
      for i in obj:
          if i['job']=='Director':
              l.append(i['name'])
              break
    except:
      pass
    return l


"""# Set up API Call Functions"""

def get_movie_data(all_movies):
    with FuturesSession() as session:
        futures = [session.get("http://128.2.204.215:8080/movie/"+title_year) for title_year in all_movies]
        for future in as_completed(futures):
            response_results = future.result().json()

            if "message" not in response_results:
                title_year_val = response_results["id"]
                fields_we_care_about = ["tmdb_id","title","overview","genres","popularity","release_date","runtime","vote_average","vote_count"]
                final_entry = {}
                final_entry["title_year"] = title_year_val
                for field in fields_we_care_about:
                    try:
                        this_field_data = response_results[field]
                        if field == "tmdb_id":
                            tmdb_to_title_year[response_results["tmdb_id"]] = title_year_val
                        elif field == "genres":
                            this_field_data = convert_to_more_readable(this_field_data)
                            this_field_data = remove_spaces(this_field_data)

                        final_entry[field] = this_field_data
                    except:
                        pass

                data_to_append[title_year_val] = final_entry
            else:
                print("issue loading this json into data frame:",response_results)

    return True


def get_keywords_from_api(tmdb_list):
    with FuturesSession() as session:
        futures = [session.get("https://api.themoviedb.org/3/movie/"+str(tmdb_id)+"/keywords?api_key=a731ea0ccfac42bffc929317ddc7f94f&query&language=en-US") for tmdb_id in tmdb_list]
        for future in as_completed(futures):
            response_results = future.result().json()

            if "status_message" not in response_results:
                tmdb_id_val = response_results["id"]
                title_year_val = tmdb_to_title_year[tmdb_id_val]
                try:
                    this_field_data = response_results["keywords"]
                    this_field_data = convert_to_more_readable(this_field_data)
                    this_field_data = remove_spaces(this_field_data)
                    data_to_append[title_year_val]["keywords"] = this_field_data
                except:
                    pass
            else:
                print("issue loading this json into data frame:",response_results)

    return True

def get_cast_and_crew_from_api(tmdb_list):
    with FuturesSession() as session:
        futures = [session.get("https://api.themoviedb.org/3/movie/"+str(tmdb_id)+"/credits?api_key=a731ea0ccfac42bffc929317ddc7f94f&query&language=en-US") for tmdb_id in tmdb_list]
        for future in as_completed(futures):
            response_results = future.result().json()

            if "status_message" not in response_results:
                tmdb_id_val = response_results["id"]
                title_year_val = tmdb_to_title_year[tmdb_id_val]
                fields_we_care_about = ["cast","crew"]
                for field in fields_we_care_about:
                    try:
                        this_field_data = response_results[field]
                        if field=="cast":
                            this_field_data = getcast(this_field_data)
                        elif field=="crew":
                            this_field_data = getdir(this_field_data)
                        data_to_append[title_year_val][field] =this_field_data
                    except:
                        pass

            else:
                print("issue loading this json into data frame:",response_results)

    return True

get_movie_data(movies_to_add)

list_of_tmdb_ids = tmdb_to_title_year.keys()
get_keywords_from_api(list_of_tmdb_ids)
get_cast_and_crew_from_api(list_of_tmdb_ids)

new_movie_df = pd.DataFrame(data_to_append.values())

all_movies_df = pd.concat([old_movie_df,new_movie_df], axis=0, ignore_index=True)

all_movies_df.to_csv("../csvs/movie_data.csv", index=False)


end_time = time.time()
print("it took",end_time-start_time,"seconds to gather data on",len(movies_to_add),"movies")