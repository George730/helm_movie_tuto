from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
import time

start_time = time.time()


import pandas as pd

all_data = []
missing_users_in_a_row = 0

spacing = 100100

start_loc = 0
end_loc = spacing

for i in range(10):

    with FuturesSession() as session:
        #futures = [session.get("http://128.2.204.215:8080/user/"+str(int(i))) for i in range(1000000)]

        futures = []
        for i in range(start_loc,end_loc):
            futures.append(session.get("http://128.2.204.215:8080/user/"+str(int(i))))
            if missing_users_in_a_row > 5:
                break

        for future in as_completed(futures):
            response_results = future.result().json()

            if "message" not in response_results:
                all_data.append(response_results)
                missing_users_in_a_row = 0
            else:
                missing_users_in_a_row += 1
                print("issue loading this json into data frame:",response_results)
        
        start_loc += spacing
        end_loc += spacing

        print("finished round",i+1)

user_data=pd.DataFrame(all_data)

user_data.to_csv("../csvs/user_data.csv", index=False)

end_time = time.time()

print("it took",end_time-start_time,"seconds to re-gather data on",len(all_data),"users")