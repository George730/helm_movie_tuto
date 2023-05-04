import pandas as pd
from ast import literal_eval
import argparse

import warnings
warnings.filterwarnings("ignore")

def get_movie_watch_time_metrics(new_data_df, col_name="max_minute_watched"):
    """
    Get mean and standard deviation of total movie watch time
    """
    mean = new_data_df[col_name].mean(skipna=True)
    std = new_data_df[col_name].std(skipna=True)
    return mean, std

def get_user_ratings_metrics(new_data_df):
    """
    Get mean and standard deviation of all user ratings
    """
    mean = new_data_df["user_rating"].mean(skipna=True)
    std = new_data_df["user_rating"].std(skipna=True)
    return mean, std

def apply_literal_eval(x):
    if pd.isna(x):
        return None
    return literal_eval(x)

def get_top_popular_cast(new_data_df, rating_df, n=5, based_on="user_rating"):
    """
    Get n cast who have highest values for based_on column
    """
    cast_df = new_data_df[["title_year", "cast"]].merge(rating_df[["title_year", based_on]], on="title_year", how="inner")
    cast_df = cast_df[["cast", based_on]]
    cast_df["cast"] = cast_df["cast"].apply(apply_literal_eval)

    top_casts = cast_df.explode("cast").groupby(
        "cast").mean().sort_values("user_rating", ascending=False).head(n).index.values
    return top_casts


def get_top_popular_crew(new_data_df, rating_df, n=5, based_on="user_rating"):
    """
    Get n crew who have highest values for based_on column
    """
    crew_df = new_data_df[["title_year", "crew"]].merge(rating_df[["title_year", based_on]], on="title_year",
                                                        how="inner")

    crew_df = crew_df[["crew", based_on]]
    crew_df["crew"] = crew_df["crew"].apply(apply_literal_eval)

    top_crews = crew_df.explode("crew").groupby(
        "crew").mean().sort_values("user_rating", ascending=False).head(n).index.values
    return top_crews


# includes data distribution metrics and results from last time the model was trained
baseline_result_file = "baseline_result.txt"

lines = []
with open(baseline_result_file, 'r') as f:
    lines = f.readlines()

baseline_results = {}
for line in lines:
    key, value = line.strip().split(":")
    baseline_results[key] = literal_eval(value)

parser = argparse.ArgumentParser(description='Check if there is data drift in new data')
parser.add_argument('-mf', '--moviefile', help='relative path to new movie data csv')
parser.add_argument('-rf', '--ratingfile', help='relative path to new rating data csv')
parser.add_argument('-wf', '--watchfile', help='relative path to new rating data csv')

args = parser.parse_args()

movie_df = pd.read_csv(args.moviefile)
rating_df = pd.read_csv(args.ratingfile)
watch_df = pd.read_csv(args.watchfile)

movie_df = movie_df[["title_year", "cast", "crew"]]

rating_df = rating_df[["title_year", "user_rating"]]


watch_df = watch_df[["title_year", "max_minute_watched"]]

needNewTraining = False

watch_m, watch_s = get_movie_watch_time_metrics(watch_df)

ml = baseline_results["movie_watch_mean"] - baseline_results["movie_watch_std"]
mh = baseline_results["movie_watch_mean"] + baseline_results["movie_watch_std"]

print("*" * 25)
print("Average Movie Watch Time:", watch_m)
print("Standard Deviation in Movie Watch Time:", watch_s)
print("*" * 25)
print("\n")

if watch_m < ml or watch_m > mh:
    needNewTraining = True

rating_m, rating_s = get_user_ratings_metrics(rating_df)


print("*" * 25)
print("Average User rating:", rating_m)
print("Standard Deviation in User Rating:", rating_s)
print("*" * 25)
print()

rl = baseline_results["user_rating_mean"] - baseline_results["user_rating_std"]
rh = baseline_results["user_rating_mean"] + baseline_results["user_rating_std"]

if rating_m < rl or rating_m > rh:
    needNewTraining = True

n = 100
top_casts = get_top_popular_cast(movie_df, rating_df, n=n, based_on="user_rating")

print("*" * 25)
print("Popular casts:")
count = 0
for cast in baseline_results["top_casts"]:
    print("\t", cast)
    if cast in top_casts:
        count += 1
print("*" * 25)
print()

if count < (n // 2):
    needNewTraining = True

n = 100
top_crews = get_top_popular_crew(movie_df, rating_df, n=n, based_on="user_rating")
count = 0
print("*" * 25)
print("Popular Crew:")
for crew in baseline_results["top_crews"]:
    print("\t", crew)
    if crew in top_crews:
        count += 1
print("*" * 25)

if count < (n // 2):
    needNewTraining = True

if needNewTraining:
    print("YOU NEED TO TRAIN YOUR MODEL AGAIN!!")
    ## call the pipeline job
