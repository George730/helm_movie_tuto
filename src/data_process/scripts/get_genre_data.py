import pandas as pd
from datetime import datetime
import ast


date, time = str(datetime.now()).split()
hour = "20"#time.split(":")[0]

movie_data_file_name = "movie_data.csv"
data_file_name = date+"_"+hour+"_data.csv"
genre_file_name = "genres.csv"

#first get the movie data and new round of data
data=pd.read_csv(data_file_name, low_memory=False)
movie = pd.read_csv(movie_data_file_name)
genre = pd.read_csv(genre_file_name)

#merge them
augmented_data = data.merge(movie, on="title_year", how="left")

#get all the genres counts
all_genres = {}
all_genres["DTG"] = date+"_"+hour

for list_of_genres in augmented_data["genres"]:
    try:
        actual_list_of_genres = ast.literal_eval(list_of_genres)
        for i in actual_list_of_genres:
            if i not in all_genres:
                all_genres[i] = 0
            all_genres[i] += 1
    except:
        pass

genre = pd.concat([genre, pd.DataFrame(all_genres, index=[0])], ignore_index=True)

genre.to_csv(genre_file_name,index=False)




