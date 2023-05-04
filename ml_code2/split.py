import pandas as pd
import random

user = pd.read_csv("../data_files/user_data.csv")
rating = pd.read_csv("../data_files/2023-03-27_16_rating.csv")
movie = pd.read_csv("../data_files/movie_data.csv")


ratings_with_user_with_data = rating.merge(movie,on="title_year", how="left").merge(user, on='user_id', how='left')


ratings_with_user_with_data['hashed_user_id'] = ratings_with_user_with_data.apply(lambda x: hash(x['user_id'])%100 , axis=1)

train_numbers = set()
val_numbers = set()
test_numbers = set()

remaining_numbers = []
for i in range(100):
    remaining_numbers.append(i)

for i in range(70):
    this_num = random.choice(remaining_numbers)
    remaining_numbers.remove(this_num)
    train_numbers.add(this_num)

for i in range(20):
    this_num = random.choice(remaining_numbers)
    remaining_numbers.remove(this_num)
    val_numbers.add(this_num)

for i in range(10):
    this_num = random.choice(remaining_numbers)
    remaining_numbers.remove(this_num)
    test_numbers.add(this_num)

#make sure there are no overlaps
num_overlap_train_and_val = len(train_numbers.intersection(val_numbers))
num_overlap_train_and_test = len(train_numbers.intersection(test_numbers))
num_overlap_val_and_test = len(val_numbers.intersection(test_numbers))
assert num_overlap_train_and_test == 0
assert num_overlap_train_and_val == 0
assert num_overlap_val_and_test == 0


train_data = ratings_with_user_with_data[ratings_with_user_with_data['hashed_user_id'].isin(list(train_numbers))]
val_data = ratings_with_user_with_data[ratings_with_user_with_data['hashed_user_id'].isin(list(val_numbers))]
test_data = ratings_with_user_with_data[ratings_with_user_with_data['hashed_user_id'].isin(list(test_numbers))]

train_data = train_data.drop(["hashed_user_id", "DTG"], axis = 1)
val_data = val_data.drop(["hashed_user_id", "DTG"], axis = 1)
test_data = test_data.drop(["hashed_user_id", "DTG"], axis = 1)

train_data.to_csv("train_data.csv",index=False)
val_data.to_csv("validation_data.csv",index=False)
test_data.to_csv("test_data.csv",index=False)