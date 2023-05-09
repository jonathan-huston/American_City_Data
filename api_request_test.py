#! python3
import requests
import json

def submit_query(request_str):
    response = requests.get(request_str, verify=False)
    return response.json()

if __name__ == '__main__':
    request_str = 'http://flip3.engr.oregonstate.edu:54546/api/data?state=VA&var=S1701_C03_001E'
    results_a = submit_query(request_str)
    print('\nRaw results: {0}'.format(results_a))
    print('The percent of the population below the poverty line in {0} is {1}%.\n'.format(results_a['state'], results_a['value']))
    request_str = 'http://flip3.engr.oregonstate.edu:54546/api/data?state=PR&var=S2301_C04_001E'
    results_b = submit_query(request_str)
    print('Raw results: {0}'.format(results_b))
    print('The unemployment rate in {0} is {1}%.\n'.format(results_b['state'], results_b['value']))