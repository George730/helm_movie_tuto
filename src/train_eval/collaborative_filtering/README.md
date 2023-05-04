# Recommendation System

## Collaborative Filtering

We use the combined data of user and movies to extract user_id, movie_id and user_rating for the movie. A user-movie interaction matrix is constructed using the ratings given by users for the movies.
In case of multiple ratings for a movie by same user, mean of ratings is taken.

We notice that most entries in the ratings matrix are 0 because every user only rates a very small subset of all movies. We can leverage this observation to only store the non-zero entries of the matrix in a form known as "sparse" form.
Further we use matrix factorization of sparse matrix into user matrix and movie matrix with feature vector length of 10.

User-Movie Matrix = User Matrix @ Movie Matrix

Note: '@' represents matrix multiplication

To recommend movies for a user, we construct the user-movie matrix from lower rank matrices and return the top 20 movie ids from the predicted ratings (movies that the user never rated).
For new users, we pick the most popular 20 movies among all existing users. This results in all new users getting the same recommendation until the model is updated with new data.

## Instructions

```commandline
$ cd ml_code
$ python collaborative_filtering.py  # to train model
$ python recommend.py [user_id] # to get recommendation
```

To use the method, import recommend as module and call
```
movie_ids = get_recommendations(user_id)
```