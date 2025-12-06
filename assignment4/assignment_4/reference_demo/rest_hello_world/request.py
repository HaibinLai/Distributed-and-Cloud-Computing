import requests
import json

url = 'http://localhost:8081'  # server url

# GET on root

print("GET request on the root endpoint")

r = requests.get(url)
print('server response:', r.json())

# GET on /chat/George

print("GET request at endpoint /chat/george")

endpoint = "/chat/George"  # endpoint name to append to server url

r = requests.get(url + endpoint, params={'institution': 'SUSTech'})
print('server response:', r.json())

# POST on /calculator/mult

print("POST data in JSON format at endpoint /calculator/mult")

endpoint = '/calculator/mult'  # endpoint name to append to server url

# json files required for POST requests
#   headers: defines data type for 'data'
#   data: the data to be posted)
headers = {"Content-Type": "application/json"}
data = {"xin": 2, "yin": 10}

r = requests.post(url + endpoint, headers=headers, data=json.dumps(data))
print('server response:', r.json())
