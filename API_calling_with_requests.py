'''
Script that uses fake API to fetch data from JSONPlaceholder server.
Popular status codes are as follows:
1. 200 OK
2. 400 Bad Request (server couldn't understand the request)
3. 401 Unauthorized (authentication needed)
4. 404 Not Found (The requested resource could not be found)
5. 500 Internal Server Error (server encountered an error)
6. 201 Created

'''

import requests
import pandas as pd
import numpy as np
import json
# from bs4 import BeautifulSoup

# make API call to fetch user information using GET
URL = 'https://jsonplaceholder.typicode.com/users'
PATH_TO_FILE = 'users.json'
response = requests.get(URL)

if response.status_code == 200:
    with open(PATH_TO_FILE, 'w') as f:
        json.dump(response.json(), f)

# post data to server using POST
URL = 'https://jsonplaceholder.typicode.com/posts'
data_to_post = {
    'car':['Mahindra','Hyundai','Maruti'],
    'Planes':['Sukoi','Raffael']
}
post_response = requests.post(URL,data=data_to_post)
if post_response.status_code == 201:
    print(f'Successfully posted! {post_response.json()}')
else:
    print('Something went wrong in posting!')



