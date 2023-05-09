#! python3
import requests
import json

def submit_query(request_str):
    response = requests.get(request_str, verify=False)
    return response.json()

if __name__ == '__main__':
    request_str = 'http://flip3.engr.oregonstate.edu:54546/api/data?state=VA&var=S1701_C03_001E'
    results = submit_query(request_str)
    print(results)