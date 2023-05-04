import sys
import pandas as pd
# from prometheus_client import Gauge, start_http_server, CollectorRegistry 

# AVERAGE_PERCENT_MOVIE_WATCHED_FROM_ONLINE = Gauge(
#     'percent_movie_watched', 'Percent Movie Watched Online Metric',
#     ['movie_percent']
# )

# PERCENT_RECOMMENDATIONS_WATCHED_FROM_ONLINE = Gauge(
#     'percent_recommendation_watched', 'Percent of Recommendations Watched Online Metric',
#     ['recommendation_percent']
# )

# AVERAGE_RATING_FROM_ONLINE = Gauge(
#     'average_rating_from_online', 'Average Rating Online Metrics',
#     ['rating_val']
# )
# FINAL_SCORE = Gauge(
#     'final_score', 'Final Score Vals Online Metric',
#     ['score_val']
# )

# registry = CollectorRegistry()
# registry.register(FINAL_SCORE)
# registry.register(AVERAGE_RATING_FROM_ONLINE)
# registry.register(PERCENT_RECOMMENDATIONS_WATCHED_FROM_ONLINE)
# registry.register(AVERAGE_PERCENT_MOVIE_WATCHED_FROM_ONLINE)

# start_http_server(8765, registry=registry)

def recommendations_watched(df_filtered,recommend):
    counts = df_filtered.groupby('user_id').size().reset_index(name='count')
    percentage_of_recommendations_watched = counts['user_id'].nunique()/recommend['user_id'].nunique()
    print(f"Percentage of recommendations watched {percentage_of_recommendations_watched:.2f}")
    return percentage_of_recommendations_watched
    
def average_rating(df_filtered_rating):
    rating_average = df_filtered_rating['user_rating'].mean()
    print(f"Average ratings for all movies {rating_average:.2f}")
    return rating_average
    
def percent_movie(merged_df_movies):
    avg_percentage_movie_watched = merged_df_movies['movie_watched'].mean()
    print(f"Percentage of movies watched by movies {avg_percentage_movie_watched:.2f}")
    return avg_percentage_movie_watched

def get_filtered_df(data, recommend):
    #Merge the datasets to get tables to find the recommendations watched
    melted_recommend = recommend.melt(id_vars='user_id', value_vars=recommend.iloc[:, 2:24])
    merged_df = pd.merge(data, melted_recommend,on='user_id', how='inner')
    df_filtered = merged_df[merged_df['title_year'] == merged_df['value']]
    df_filtered.drop_duplicates(subset=['user_id', 'value'], inplace=True)
    return df_filtered, melted_recommend

def get_filtered_rating(rating, melted_recommend):
    #merge dataset to get table for average ratings
    merged_df_rating = pd.merge(rating, melted_recommend,on='user_id', how='inner')
    df_filtered_rating = merged_df_rating[merged_df_rating['title_year'] == merged_df_rating['value']]
    df_filtered_rating.drop_duplicates(subset=['user_id', 'value'], inplace=True)
    return df_filtered_rating
    
def get_merged_movies(movie_data, df_filtered):
    merged_df_movies = pd.merge(movie_data, df_filtered,on='title_year', how='inner')
    merged_df_movies['movie_watched'] = merged_df_movies['max_minute_watched'] / merged_df_movies['runtime']
    return merged_df_movies


def calculate_score(df_filtered, df_filtered_rating, merged_df_movies, recommend):
    # final score computation (weighted average)
    #50% weight on number of recommendations watched, 30% weight on time watched, and 20% weight on user rating

    percentage_of_recommendations_watched = recommendations_watched(df_filtered,recommend)
    # PERCENT_RECOMMENDATIONS_WATCHED_FROM_ONLINE.labels(rating_val).set(rating_average)
        
    rating_average = average_rating(df_filtered_rating)
    # AVERAGE_RATING_FROM_ONLINE.labels(rating_val).set(rating_average)
    
    avg_percentage_movie_watched = percent_movie(merged_df_movies)
    # AVERAGE_PERCENT_MOVIE_WATCHED_FROM_ONLINE.labels(percent_watched).set(avg_percentage_movie_watched)
    
    num_rec_watched_weight = 0.5
    weight_time_watched = 0.3
    weight_rating = 0.2
    
    final_score = (percentage_of_recommendations_watched*num_rec_watched_weight)+(rating_average/5)*weight_rating+(avg_percentage_movie_watched*weight_time_watched)
    # FINAL_SCORE.labels(score_val).set(final_score)
    
    return final_score

def main():
    pd.options.mode.chained_assignment = None
    rating = pd.read_csv(sys.argv[1])
    recommend = pd.read_csv(sys.argv[2])
    data = pd.read_csv(sys.argv[3])
    movie_data = pd.read_csv("movie_data.csv")
    
    data = data[data['max_minute_watched'] >= 20]
    
    df_filtered, melted_recommend = get_filtered_df(data, recommend)
    df_filtered_rating = get_filtered_rating(rating, melted_recommend)
    merged_df_movies = get_merged_movies(movie_data, df_filtered)

    final_score = calculate_score(df_filtered, df_filtered_rating, merged_df_movies, recommend)
        
    print(f"The final score is {final_score:.2f}")

if __name__ == "__main__":
    main()
