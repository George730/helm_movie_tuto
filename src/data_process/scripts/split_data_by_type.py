from datetime import datetime
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-u", "--unit_test", action="store_true")
args = parser.parse_args()

#get the time
date, time = str(datetime.now()).split()
hour = time.split(":")[0]


if args.unit_test == True:
  #open files in pytest folder
  combined_file_name = "tests/data_preprocess/"+date+"_"+ hour +".csv"
  rating_file_name = "tests/data_preprocess/"+date+"_"+hour+"_rating.csv"
  recommendation_file_name = "tests/data_preprocess/"+date+"_"+hour+"_recommend.csv"
  data_file_name = "tests/data_preprocess/"+date+"_"+hour+"_data.csv"

  movie_update_file = open("tests/data_preprocess/movie_update_file.txt","w")
  bad_line_file = open("tests/data_preprocess/"+date+"_"+hour+"_bad_line_file.txt","w")
 
else:
  #open all the files in normal location
  combined_file_name = "../csvs/"+date+"_"+ hour +".csv"
  rating_file_name = "../csvs/"+date+"_"+hour+"_rating.csv"
  recommendation_file_name = "../csvs/"+date+"_"+hour+"_recommend.csv"
  data_file_name = "../csvs/"+date+"_"+hour+"_data.csv"

  movie_update_file = open("../csvs/movie_update_file.txt","w")
  bad_line_file = open("../csvs/"+date+"_"+hour+"_bad_line_file.txt","w")
  
combined_file = open(combined_file_name, "r")
ratings_file = open(rating_file_name,"w")
recommend_file = open(recommendation_file_name, "w")
data_file = open(data_file_name, "w")

#create holders for unique movies, bad lines, and user movie pairs
unique_movies = set()
bad_lines = []
data_shrinker = {}

def recommendation_function(row):
  new_row = ""
  try:
    split_row = row.split(",")
    '''try:
        assert(len(split_row) == 25)
    except AssertionError as msg:
        print(split_row)'''
    if(len(split_row) == 25):
      new_row += split_row[0] +"," #DTG
      new_row += str(int(float(split_row[1]))) + "," #userid
      bogus_text,first_rec = split_row[4].split()
      new_row += first_rec + ","
      for i in range(5,24):
        new_row += split_row[i]
        if i != 23:
          new_row += ","
      new_row += "\n"
  except:
     new_row = ""
     bad_lines.append(row)
     
  return new_row
def data_function(row):
  try:
    split_row = row.split(",")
    day_time_group = split_row[0]
    user_id = str(int( split_row[1] ))
    split_row2 = split_row[2].split("/")
    #print(split_row2)i
    #assert(split_row2[0] == "GET"), ("("+split_row2[0]+")")
    #assert(split_row2[1] == "data")
    #assert(split_row2[2].strip() == "m"), split_row2[2]
    if("GET" in split_row2[0] and split_row2[2] == "m"):
      movie_title = split_row2[3]
      #print(split_row2)
      mpg_minute, mpg_bit = split_row2[4].split(".")
      #mpg_minute = re.sub("\D","", mpg_minute)
      # ignore since file format does not matter
      #assert(mpg_bit == "mpg"), mpg_bit
      mpg_minute = int(float(mpg_minute))
      if (mpg_minute > 1440):
         raise ValueError
      new_line = day_time_group + "," + user_id + "," + movie_title + "," + str(mpg_minute) +"\n"
      if user_id not in data_shrinker:
          data_shrinker[user_id] = {}
      if movie_title not in data_shrinker[user_id]:
          data_shrinker[user_id][movie_title] = (mpg_minute, new_line)
      elif data_shrinker[user_id][movie_title][0] < mpg_minute:
          data_shrinker[user_id][movie_title] = (mpg_minute, new_line)
      unique_movies.add(movie_title)
  except:
    bad_lines.append(row)
  

def rating_function(row):
  new_row = ""
  try:
    split_row = row.split(",")
    new_row += split_row[0] + ","
    new_row += str(int(float(split_row[1]))) + ","
    split_row2 = split_row[2].split("/")
    #print(split_row2)
    #assert(split_row2[0] =="GET " ), split_row2[0]
    #assert(split_row2[1] == "rate")
    #if("GET" in split_row2[0]):
    movie_title, rating = split_row2[2].split("=")
    new_row += movie_title +","
    new_row += str(int(float(rating)))+"\n"
    unique_movies.add(movie_title)
  except:
     new_row = ""
     bad_lines.append(row)
  return new_row

#set up the first row in every csv
data_cols = "DTG,user_id,title_year,max_minute_watched\n"
rating_cols = "DTG,user_id,title_year,user_rating\n"
recommend_cols = "DTG,user_id,rec1,rec2,rec3,rec4,rec5,rec6,rec7,rec8,rec9,rec10,rec11,rec12,rec13,rec14,rec15,rec16,rec17,rec18,rec19,rec20\n"
data_file.write(data_cols)
ratings_file.write(rating_cols)
recommend_file.write(recommend_cols)

#loop through the big mess of data and sort it out
for line in combined_file:
    line = line.strip()
    if "/data/" in line:
        data_function(line)
    elif "/rate/" in line:
        new_line = rating_function(line)
        ratings_file.write(new_line)
    elif "recommendation request" in line and "TimeoutException" not in line:
        new_line = recommendation_function(line)
        recommend_file.write(new_line )
    else:
       bad_lines.append(line)

#for each max minute movie user pair, write to the file
for movie_dict in data_shrinker.values():
   for (minutes, new_line) in movie_dict.values():
      data_file.write(new_line)

#close all the files
ratings_file.close()
recommend_file.close()
data_file.close()
combined_file.close()

#for each unique movie write to the file
for movie in unique_movies:
   movie_update_file.write(movie+"\n")
movie_update_file.close()

#for each bad line write to the file
for line in bad_lines:
   bad_line_file.write(line + "\n")
bad_line_file.close()