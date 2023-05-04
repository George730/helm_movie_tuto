# Notes on the Data Thus Far:

### Process:

1. Run this Command:
```{
ssh -o ServerAliveInterval=60 -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf}```

2. Run the script get_data_from_kafka.py. This will return two CSV's (kafka_movielog_data.csv and kafka_movielog_rate.csv)
3. Take the two CSV's and run them through the corresponding and Augmenting script.
    - requests for data go to kafka_augment_data.py
    - requests for ratings go to kafka_augment_rate.py
4. This returns 4 CSVs: 10000_augmented_kafka_data.csv (some columns still have jsons from tmdb data base), 10000_augmented_kafka_rate.csv(some columns still have jsons from tmdb data base), 10000_augmented_mediumclean_kafka_data.csv, 10000_augmented_mediumclean_kafka_rate.csv

### get_data_from_kafka.py:
- currently set up to get 10,000 data samples for data requests and 10,000 data samples for rate requests
- must be sshed into kafka for this to work

### Augmenting scripts:
- Basically take each row, figure out what the movie title corresponds to in the tmdb database and pulls the corresponding data (such as cast, genre, keywords, etc.) It also pulls the user demographic data (sucha as gender)
- Doesn't remove any requests, but tmdb does lack certain entries. This results in some empty fields


### Columns in the CSVs and What They Mean


| Column Name | Description | Col In TMDB.csv | Col In Data.csv | Col In Rate.csv|
| --- | ----------- |----|----|----|
| DTG | Date/Time that the request was made |No|Yes|Yes|
| cast | Top 3 Actors in the Movie |Yes|Yes|Yes|
| crew |Director of the movie|Yes|Yes|Yes|
| genres | Top 3 genres to describe the Movie |Yes|Yes|Yes|
| keywords | keywords to describe the movie |Yes|Yes|Yes|
| minute_watched | What minute of the movie was the data requested for (we get one per minute) |No|Yes|No|
| movie_id |TMDB id for this movie|Yes|Yes|Yes|
| overview | Summary of the movie |Yes|Yes|Yes|
| popularity | popularity according to TMDB |Yes|Yes|Yes|
| release_date | Date the movie was released|Yes|Yes|Yes|
| runtime |How long the movie is|Yes|Yes|Yes|
| title | Movie title |Yes|Yes|Yes|
| user_id | What user was interacting with the movie |No|Yes|Yes|
| vote_average | the average vote value given to this movie on TMDB |Yes|Yes|Yes|
| vote_total | the total number of votes for this movie|Yes|Yes|Yes|
| year |year this movie came out|Yes|Yes|Yes|
| user_rating | what the user rated this movie |No|No|Yes|
| user_gender | gender of the user|Yes|Yes|Yes|
| user_age |age of the user|Yes|Yes|Yes|
| user_occupation | what the user does as a job |Yes|Yes|Yes|

